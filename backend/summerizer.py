import json

import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "/Users/darshankareliya/.cache/huggingface/hub/models--HuggingFaceTB--SmolLM2-135M-Instruct/snapshots/12fd25f77366fa6b3b4b768ec3050bf629380bac"
BASE_DIR = Path(__file__).resolve().parent
# JSON_FILE = BASE_DIR / "data" / "2fcb19b2-9e73-4080-9c9a-c73154e40fd2.json"

JSON_FILE = "data/analyses/2fcb19b2-9e73-4080-9c9a-c73154e40fd2.json"

# Keep this comfortably below the model's 8192-token context.
CHUNK_SIZE = 3500

# Number of tokens generated for each intermediate summary.
SUMMARY_TOKENS = 300

# Number of tokens generated for the final summary.
FINAL_SUMMARY_TOKENS = 500


# ============================================================
# Device
# ============================================================

if torch.backends.mps.is_available():
    device = torch.device("mps")
    dtype = torch.float16
    print("Using Apple Metal (MPS)")
else:
    device = torch.device("cpu")
    dtype = torch.float32
    print("Using CPU")


# ============================================================
# Load model
# ============================================================

print("Loading model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    dtype=dtype,
)

model.to(device)
model.eval()

print("Model loaded.")


# ============================================================
# Load JSON
# ============================================================

print(f"Loading JSON: {JSON_FILE}")

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

json_text = json.dumps(
    data,
    ensure_ascii=False,
    indent=2
)

print(f"JSON characters: {len(json_text):,}")


# ============================================================
# Tokenize entire JSON
# ============================================================

json_tokens = tokenizer.encode(
    json_text,
    add_special_tokens=False
)

print(f"JSON tokens: {len(json_tokens):,}")


# ============================================================
# Split into chunks
# ============================================================

chunks = []

for i in range(0, len(json_tokens), CHUNK_SIZE):
    chunk_tokens = json_tokens[i:i + CHUNK_SIZE]

    chunk_text = tokenizer.decode(
        chunk_tokens,
        skip_special_tokens=True
    )

    chunks.append(chunk_text)


print(f"Created {len(chunks)} chunks.")


# ============================================================
# Summarization function
# ============================================================

def summarize_chunk(text, chunk_number, total_chunks):

    system_prompt = """
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

### WHAT THE REVIEW SHOULD ANSWER

The 3–4 sentences should communicate:

* **Overall customer reaction:** Are customers mainly satisfied, dissatisfied, or mixed?
* **Main problems:** What are the most important recurring issues?
* **Customer needs:** What do customers appear to want improved?
* **Business implication:** What should the product/company team pay attention to or prioritize?

### OUTPUT REQUIREMENTS

Return **exactly 3 or 4 sentences**.

Write in a professional, concise, business-oriented style suitable for a product manager or company executive.

The review should be specific rather than generic.

Prefer statements such as:

"Customers are primarily concerned about..."

"The most frequent feedback relates to..."

"Several comments indicate..."

"This suggests the company should prioritize..."

Avoid vague statements such as:

"Customers have mixed opinions."

"The feedback is important."

"There are several issues that need attention."

Do not use bullet points, headings, labels, JSON, or markdown.

### IMPORTANT

The numerical data describes the overall feedback, while the individual comments provide examples and context.

Do not assume that the few comments included in `comments` represent the entire dataset. Use the aggregate counts to describe overall trends and use the comments to explain or illustrate those trends.

If aggregate data and individual comments appear inconsistent, prioritize the aggregate data for overall trends and use the comments only for qualitative context.

### JSON INPUT

{INPUT_JSON}

### FINAL OUTPUT

Return only the 3–4 sentence product feedback review.

"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": (
                f"This is chunk {chunk_number} of {total_chunks} "
                "from a larger JSON dataset.\n\n"
                "Summarize this chunk:\n\n"
                f"{text}"
            )
        }
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    )

    # Explicit attention mask fixes the warning you were seeing.
    attention_mask = torch.ones_like(inputs)

    inputs = inputs.to(device)
    attention_mask = attention_mask.to(device)

    with torch.inference_mode():

        outputs = model.generate(
            input_ids=inputs,
            attention_mask=attention_mask,

            max_new_tokens=SUMMARY_TOKENS,

            # Deterministic summarization
            do_sample=False,

            # Prevent model from generating too much
            repetition_penalty=1.05,
        )

    generated_tokens = outputs[0][inputs.shape[-1]:]

    summary = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    ).strip()

    return summary


# ============================================================
# Summarize each chunk
# ============================================================

chunk_summaries = []

for i, chunk in enumerate(chunks, start=1):

    print(
        f"\nSummarizing chunk {i}/{len(chunks)}..."
    )

    summary = summarize_chunk(
        chunk,
        i,
        len(chunks)
    )

    chunk_summaries.append(summary)

    print(f"Chunk {i} summary:")
    print(summary)


# ============================================================
# Combine chunk summaries
# ============================================================

combined_summary = "\n\n".join(
    f"Summary {i + 1}:\n{summary}"
    for i, summary in enumerate(chunk_summaries)
)

print(
    f"\nCombined summary tokens: "
    f"{len(tokenizer.encode(combined_summary)):,}"
)


# ============================================================
# Final summarization
# ============================================================

final_system_prompt = """
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

final_messages = [
    {
        "role": "system",
        "content": final_system_prompt
    },
    {
        "role": "user",
        "content": (
            "Create a final summary from these "
            "section summaries:\n\n"
            f"{combined_summary}"
        )
    }
]


# ------------------------------------------------------------
# Check final input size
# ------------------------------------------------------------

final_inputs = tokenizer.apply_chat_template(
    final_messages,
    add_generation_prompt=True,
    return_tensors="pt"
)

final_attention_mask = torch.ones_like(final_inputs)

final_inputs = final_inputs.to(device)
final_attention_mask = final_attention_mask.to(device)


print(
    f"Final prompt tokens: "
    f"{final_inputs.shape[-1]:,}"
)


# ============================================================
# Generate final summary
# ============================================================

with torch.inference_mode():

    final_outputs = model.generate(
        input_ids=final_inputs,
        attention_mask=final_attention_mask,

        max_new_tokens=FINAL_SUMMARY_TOKENS,

        do_sample=False,

        repetition_penalty=1.05,
    )


# ============================================================
# Decode final summary
# ============================================================

final_generated_tokens = final_outputs[0][
    final_inputs.shape[-1]:
]

final_summary = tokenizer.decode(
    final_generated_tokens,
    skip_special_tokens=True
).strip()


# ============================================================
# Save result
# ============================================================

OUTPUT_FILE = BASE_DIR / "data" / "summary.txt"

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(final_summary)


print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)
print(final_summary)
print("=" * 60)

print(f"\nSaved to: {OUTPUT_FILE}")