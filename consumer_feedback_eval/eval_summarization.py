"""
Evaluation for Model 3: HuggingFaceTB/SmolLM2-135M

Note: this is the base (non-instruct) pretrained checkpoint, so it is
prompted as a plain text-completion model rather than through a chat
template. Expect noticeably weaker summaries than an instruction-tuned
model such as SmolLM2-135M-Instruct (which is what the dashboard's own
backend/summery_generator.py actually uses) — that gap is itself a
useful finding to note in the report.

Metrics reported:
  - ROUGE-1 / ROUGE-2 / ROUGE-L (precision, recall, f-measure)
  - BERTScore (precision, recall, F1) — semantic similarity to the reference

Run:
    python eval_summarization.py
"""

import json
import re

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from metrics_utils import rouge_report, bertscore_report, save_json

MODEL_NAME = "/Users/darshankareliya/.cache/huggingface/hub/models--HuggingFaceTB--SmolLM2-135M-Instruct/snapshots/12fd25f77366fa6b3b4b768ec3050bf629380bac"
GOLD_JSON = "data/summarization_gold.json"
RESULTS_DIR = "results"
MAX_NEW_TOKENS = 60

PROMPT_TEMPLATE = (
    "Summarize the following customer feedback comments about {keyword} "
    "in one or two sentences.\n\nComments:\n{source_text}\n\nSummary:"
)


def load_model():
    print(f"Loading model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    return tokenizer, model, device


def clean_generated_summary(text):
    """Keep only the first summary the model produces, before it drifts off
    into a new 'Comments:' block or repeats the prompt structure."""
    text = text.strip()
    for stop_marker in ["\nComments:", "\nSummarize", "\n\n"]:
        if stop_marker in text:
            text = text.split(stop_marker)[0].strip()
    # Collapse to the first 1-2 sentences if the model rambles on.
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return " ".join(sentences[:3]).strip()


def generate_summary(entry, tokenizer, model, device):
    prompt = PROMPT_TEMPLATE.format(keyword=entry["keyword"], source_text=entry["source_text"])
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            repetition_penalty=1.3,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated_tokens = output_ids[0][inputs["input_ids"].shape[-1]:]
    raw_summary = tokenizer.decode(generated_tokens, skip_special_tokens=True)
    return clean_generated_summary(raw_summary)


def print_report(rouge, bert):
    print("\n" + "=" * 60)
    print("SUMMARIZATION — HuggingFaceTB/SmolLM2-135M")
    print("=" * 60)
    for k in ["rouge1", "rouge2", "rougeL"]:
        avg = rouge["averages"][k]
        print(f"{k.upper():8s} P={avg['precision']:.4f}  R={avg['recall']:.4f}  F1={avg['fmeasure']:.4f}")
    b = bert["averages"]
    print(f"\nBERTScore  P={b['precision']:.4f}  R={b['recall']:.4f}  F1={b['f1']:.4f}")
    print("=" * 60)


def main():
    with open(GOLD_JSON, "r", encoding="utf-8") as f:
        gold = json.load(f)

    tokenizer, model, device = load_model()

    predictions, references = [], []
    per_example_outputs = []
    for entry in gold:
        summary = generate_summary(entry, tokenizer, model, device)
        predictions.append(summary)
        references.append(entry["reference_summary"])
        per_example_outputs.append({
            "id": entry["id"],
            "keyword": entry["keyword"],
            "reference_summary": entry["reference_summary"],
            "generated_summary": summary,
        })
        print(f"[{entry['id']}] generated: {summary}")

    rouge = rouge_report(predictions, references)
    bert = bertscore_report(predictions, references)
    print_report(rouge, bert)

    save_json({"rouge": rouge, "bertscore": bert}, f"{RESULTS_DIR}/summarization_metrics.json")
    save_json(per_example_outputs, f"{RESULTS_DIR}/summarization_predictions.json")

    return rouge, bert


if __name__ == "__main__":
    main()
