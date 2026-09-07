"""
First call to filter_reviews() downloads the model from Hugging Face once
(a few GB), then everything runs fully offline from the local MLX cache.
"""

import json
import re
import logging

from mlx_lm import load, generate

log = logging.getLogger(__name__)

# MODEL_ID = "mlx-community/Qwen3-4B-Instruct-2507-4bit"
MODEL_ID = "/Users/darshankareliya/.cache/huggingface/hub/models--mlx-community--Qwen3-4B-Instruct-2507-4bit/snapshots/50d427756c6b1b2fe0c0a10f67fbda1fc8e82c1b"

VALID_LABELS = {"product_review", "question", "general_comment", "spam"}

PROMPT_TEMPLATE = """Classify this YouTube comment, left on a product review video, into exactly one of these categories:

product_review: the commenter shares their own experience, opinion, or feedback about actually using the product
question: the commenter is asking for information about the product or video
general_comment: a reaction to the video or channel itself, not about the product
spam: promotional, scam, or content unrelated to the product

Comment: "{text}"

Respond with only JSON in this exact shape, no other text: {{"label": "product_review" | "question" | "general_comment" | "spam", "reason": "short reason"}}"""


_model = None
_tokenizer = None


def _get_model():
    global _model, _tokenizer
    if _model is None:
        log.info("Loading %s (first call only)...", MODEL_ID)
        _model, _tokenizer = load(MODEL_ID)
    return _model, _tokenizer


def _extract_json(raw_text):
    """
    Qwen3 sometimes wraps output in markdown fences or adds a short lead-in
    despite the prompt asking for JSON only. Pull out the first {...} block
    rather than assuming the whole response is clean JSON.
    """
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError("no JSON object found in model output")
    return json.loads(match.group(0))


def _classify_single(text, model, tokenizer, retries=1):
    prompt_text = PROMPT_TEMPLATE.format(text=text.replace('"', "'"))
    messages = [{"role": "user", "content": prompt_text}]
    prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True)

    last_error = None
    for attempt in range(retries + 1):
        try:
            raw = generate(model, tokenizer, prompt=prompt, verbose=False, max_tokens=200)
            parsed = _extract_json(raw)
            label = str(parsed.get("label", "")).strip().lower()
            if label in VALID_LABELS:
                return label, parsed.get("reason", "")
            last_error = f"unexpected label: {label!r}"
        except Exception as exc:
            last_error = exc

    log.warning("Qwen3 classification failed for comment (%s): %r", last_error, text[:80])
    return "unknown", ""


def filter_reviews(comments, max_tokens=200, return_details=False):
    """
    Filters `comments` (a list of strings) down to the ones classified as
    product reviews.

    Runs sequentially, not in parallel threads. Unlike Ollama's server,
    which queues and can process multiple requests, a single loaded MLX
    model instance generates one sequence at a time on the GPU, so wrapping
    this in a ThreadPoolExecutor would not add real throughput and risks
    contention on the same model object. For a batch of a few hundred
    comments this is still fast on M-series hardware with a 4bit 4B model.

    return_details: if True, returns every comment with its assigned label
    instead of just the filtered review text list.
    """
    if not comments:
        return []

    model, tokenizer = _get_model()

    labeled = []
    for text in comments:
        label, reason = _classify_single(text, model, tokenizer)
        labeled.append({"text": text, "label": label, "reason": reason})

    if return_details:
        return labeled

    reviews = [item["text"] for item in labeled if item["label"] == "product_review"]
    log.info("Filtered messages ::::::::::", reviews)
    log.info(
        "Review filter: kept %d/%d YouTube comments as product reviews.",
        len(reviews), len(comments),
    )
    return reviews


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     sample_comments = [
#         "Hab das MacBook Air M5 seit zwei Wochen, Akku hält locker den ganzen Tag.",
#         "Wie viel RAM hat das Basismodell?",
#         "Wie gewohnt super Video, immer wieder gerne!",
#         "Kostenlose Geschenkkarte hier klicken: bit.ly/xyz",
#     ]
#     for item in filter_reviews(sample_comments, return_details=True):
#         print(f"[{item['label']}] {item['text']}  -> {item['reason']}")
