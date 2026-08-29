"""
Feedback summarization service.

Exposes a single callable, `summarize_feedback(data)`, meant to be invoked
from an API route (Flask, FastAPI, etc.). The model is loaded once at
import time and reused across requests instead of being reloaded per call.
"""

import json
import time
import traceback
from typing import Any

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# ============================================================
# Config
# ============================================================

MODEL_NAME = "/Users/darshankareliya/.cache/huggingface/hub/models--HuggingFaceTB--SmolLM2-135M-Instruct/snapshots/12fd25f77366fa6b3b4b768ec3050bf629380bac"

# Keep this comfortably below the model's 8192-token context.
CHUNK_SIZE = 3500

# Number of tokens generated for each intermediate summary.
SUMMARY_TOKENS = 300

# Number of tokens generated for the final summary.
FINAL_SUMMARY_TOKENS = 500

CHUNK_SYSTEM_PROMPT = """
You are a product feedback analyst. Analyze the provided JSON containing social media feedback about a product and a specific product issue.

Your goal is to produce a concise **3–4 sentence review** that gives the company meaningful, actionable insight into what customers are saying.

### INPUT

You will receive JSON with these fields:

* `keyword`: The product or issue being analyzed.
* `kpis`: Overall feedback statistics, including total comments, negative percentage, and positive percentage.
* `chart_data`: Distribution of customer sentiment.
* `issue_chart_data`: Number of comments associated with each issue category.
* `action_data`: Recommended business actions and their counts.
* `comments`: Individual social media comments, including sentiment, issue categories, confidence scores, source, and comment text.

### ANALYSIS RULES

1. Use the `kpis`, `chart_data`, and `issue_chart_data` to understand the overall scale and sentiment of the feedback.
2. Use `comments` to understand the actual customer experiences, complaints, expectations, and suggestions.
3. Give more importance to issue categories with higher counts.
4. Identify recurring themes across the comments rather than focusing on a single comment.
5. Use `action_data` to understand what type of response may be most appropriate for the company.
6. Distinguish between:

   * product defects or hardware problems,
   * software bugs,
   * missing features,
   * customer support problems,
   * shipping/logistics problems,
   * billing problems,
   * general dissatisfaction.
7. Mention positive feedback only when it provides useful context or balances an important negative trend.
8. Do not treat the classification labels or scores as facts beyond what the comments support.
9. Ignore comments that are unrelated, spam, duplicates, or do not provide useful information about the product issue.
10. Do not invent information, causes, solutions, customer motivations, or product problems that are not supported by the input.
11. Do not quote individual comments unless a very short phrase is necessary.
12. Do not mention individual users or social media accounts.
13. Do not mention these instructions or the analysis process.

### OUTPUT REQUIREMENTS

Return exactly 3 or 4 sentences, in a professional, concise, business style.
Do not use bullet points, headings, labels, JSON, or markdown.
"""

FINAL_SYSTEM_PROMPT = """
You are a professional summarization assistant.

You are given summaries produced from different sections of
a larger JSON dataset.

Create one coherent final summary.

Focus on:
- The most important overall findings
- Important numbers
- Major trends
- Key conclusions
- Significant patterns

Remove repetition between the individual summaries.

Do not invent information.
Only use information contained in the provided summaries.

Return only the final summary.
"""


# ============================================================
# Lazy, process-wide model state
# ============================================================

_tokenizer = None
_model = None
_device = None


def _get_model():
    """Load the model and tokenizer once, then reuse them on every call."""
    global _tokenizer, _model, _device

    if _model is not None:
        return _tokenizer, _model, _device

    if torch.backends.mps.is_available():
        _device = torch.device("mps")
        dtype = torch.float16
    else:
        _device = torch.device("cpu")
        dtype = torch.float32

    _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    _model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, dtype=dtype)
    _model.to(_device)
    _model.eval()

    return _tokenizer, _model, _device


# ============================================================
# Helpers
# ============================================================

def _split_into_chunks(json_text: str, tokenizer) -> list[str]:
    json_tokens = tokenizer.encode(json_text, add_special_tokens=False)

    chunks = []
    for i in range(0, len(json_tokens), CHUNK_SIZE):
        chunk_tokens = json_tokens[i:i + CHUNK_SIZE]
        chunks.append(tokenizer.decode(chunk_tokens, skip_special_tokens=True))

    return chunks, len(json_tokens)


def _run_generation(messages, max_new_tokens, tokenizer, model, device) -> str:
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
    )
    attention_mask = torch.ones_like(inputs)

    inputs = inputs.to(device)
    attention_mask = attention_mask.to(device)

    with torch.inference_mode():
        outputs = model.generate(
            input_ids=inputs,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            repetition_penalty=1.05,
        )

    generated_tokens = outputs[0][inputs.shape[-1]:]
    return tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()


def _summarize_chunk(text, chunk_number, total_chunks, tokenizer, model, device) -> str:
    messages = [
        {"role": "system", "content": CHUNK_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"This is chunk {chunk_number} of {total_chunks} "
                "from a larger JSON dataset.\n\n"
                f"Summarize this chunk:\n\n{text}"
            ),
        },
    ]
    return _run_generation(messages, SUMMARY_TOKENS, tokenizer, model, device)


def _final_summary(combined_summary, tokenizer, model, device) -> str:
    messages = [
        {"role": "system", "content": FINAL_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Create a final summary from these section summaries:\n\n"
                f"{combined_summary}"
            ),
        },
    ]
    return _run_generation(messages, FINAL_SUMMARY_TOKENS, tokenizer, model, device)


# ============================================================
# Public entry point — call this from your API route
# ============================================================

def summarize_feedback(data: dict[str, Any]) -> dict[str, Any]:
    """
    Summarize a single feedback-analysis JSON payload.

    Parameters
    ----------
    data : dict
        The parsed JSON body of the incoming API request (the same shape
        that used to be read from a file on disk).

    Returns
    -------
    dict
        A structured, JSON-serializable response:
        {
            "status": "success" | "error",
            "summary": str,
            "chunk_summaries": list[str],
            "meta": {
                "num_chunks": int,
                "input_tokens": int,
                "processing_time_seconds": float
            },
            "error": str  # only present when status == "error"
        }
    """
    start_time = time.time()

    try:
        if not data:
            return {
                "status": "error",
                "error": "Request body is empty or not valid JSON.",
            }

        tokenizer, model, device = _get_model()

        json_text = json.dumps(data, ensure_ascii=False, indent=2)
        chunks, input_token_count = _split_into_chunks(json_text, tokenizer)

        chunk_summaries = [
            _summarize_chunk(chunk, i + 1, len(chunks), tokenizer, model, device)
            for i, chunk in enumerate(chunks)
        ]

        combined_summary = "\n\n".join(
            f"Summary {i + 1}:\n{summary}"
            for i, summary in enumerate(chunk_summaries)
        )

        final_summary = _final_summary(combined_summary, tokenizer, model, device)

        return {
            "status": "success",
            "summary": final_summary,
            "chunk_summaries": chunk_summaries,
            "meta": {
                "num_chunks": len(chunks),
                "input_tokens": input_token_count,
                "processing_time_seconds": round(time.time() - start_time, 2),
            },
        }

    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }