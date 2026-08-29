"""
Evaluation for Model 2: cross-encoder/nli-deberta-v3-base
(used as a zero-shot classifier for multi-label issue categorization,
exactly as in backend/category.py)

Metrics reported:
  - Per-label precision / recall / F1 for each of the 6 issue categories
  - Micro-F1 and Macro-F1 across categories
  - Hamming loss and Jaccard similarity (multi-label)

Run:
    python eval_issue_categorization.py
"""

import json

import numpy as np
import torch
from transformers import pipeline

from metrics_utils import multilabel_report, save_json

MODEL_NAME = "/Users/darshankareliya/.cache/huggingface/hub/models--cross-encoder--nli-deberta-v3-base/snapshots/6c749ce3425cd33b46d187e45b92bbf96ee12ec7"
GOLD_JSON = "data/issue_categorization_gold.json"
RESULTS_DIR = "results"
THRESHOLD = 0.45  # same default threshold used in backend/category.py

# Must match ISSUE_CATEGORY_MAPPING in backend/category.py: model-facing hypothesis
# label -> business-friendly label used in the gold data and the app's output.
ISSUE_CATEGORY_MAPPING = {
    "Software bug or application malfunction": "Bug / Software Defect",
    "Hardware defect or physical product problem": "Hardware / Physical Defect",
    "Shipping, delivery, or package tracking problem": "Shipping / Delivery Delay",
    "Billing, payment, refund, or pricing dispute": "Billing / Refund Dispute",
    "Customer service or technical support problem": "Customer Service / Support Issue",
    "Missing feature or requested functionality": "Feature Request / Missing Functionality",
}
ISSUE_CATEGORIES = list(ISSUE_CATEGORY_MAPPING.keys())
LABEL_NAMES = list(ISSUE_CATEGORY_MAPPING.values())  # column order for metrics


def load_classifier():
    print(f"Loading model: {MODEL_NAME}")
    device = 0 if torch.cuda.is_available() else -1
    return pipeline("zero-shot-classification", model=MODEL_NAME, device=device)


def predict_labels(texts, classifier, batch_size=16):
    """Returns a list of sets of business-friendly labels, one set per text."""
    predictions = classifier(texts, candidate_labels=ISSUE_CATEGORIES, multi_label=True, batch_size=batch_size)
    if isinstance(predictions, dict):  # single input edge case
        predictions = [predictions]

    all_labels = []
    for pred in predictions:
        assigned = {
            ISSUE_CATEGORY_MAPPING[label]
            for label, score in zip(pred["labels"], pred["scores"])
            if score >= THRESHOLD
        }
        all_labels.append(assigned)
    return all_labels


def to_binary_matrix(list_of_label_sets, label_names):
    matrix = np.zeros((len(list_of_label_sets), len(label_names)), dtype=int)
    for i, labels in enumerate(list_of_label_sets):
        for j, name in enumerate(label_names):
            if name in labels:
                matrix[i, j] = 1
    return matrix


def print_report(report):
    print("\n" + "=" * 70)
    print("ISSUE CATEGORIZATION — cross-encoder/nli-deberta-v3-base (zero-shot)")
    print("=" * 70)
    print(f"Examples evaluated : {report['n_examples']}")
    print(f"Threshold used     : {THRESHOLD}")
    print(f"\nMicro-F1           : {report['micro_f1']:.4f}")
    print(f"Macro-F1           : {report['macro_f1']:.4f}")
    print(f"Hamming loss       : {report['hamming_loss']:.4f}")
    print(f"Jaccard (samples)  : {report['jaccard_samples_avg']:.4f}")
    print(f"Jaccard (macro)    : {report['jaccard_macro_avg']:.4f}")
    print("\nPer-label precision / recall / F1:")
    print("Label".ljust(42) + "Prec".rjust(8) + "Recall".rjust(8) + "F1".rjust(8) + "Support".rjust(10))
    for row in report["per_label"]:
        print(
            row["label"].ljust(42)
            + f"{row['precision']:.3f}".rjust(8)
            + f"{row['recall']:.3f}".rjust(8)
            + f"{row['f1']:.3f}".rjust(8)
            + str(row["support"]).rjust(10)
        )
    print("=" * 70)


def main():
    with open(GOLD_JSON, "r", encoding="utf-8") as f:
        gold = json.load(f)

    texts = [item["text"] for item in gold]
    true_label_sets = [set(item["labels"]) for item in gold]

    classifier = load_classifier()
    pred_label_sets = predict_labels(texts, classifier)

    y_true = to_binary_matrix(true_label_sets, LABEL_NAMES)
    y_pred = to_binary_matrix(pred_label_sets, LABEL_NAMES)

    report = multilabel_report(y_true, y_pred, LABEL_NAMES)
    print_report(report)

    # Save per-example predictions for qualitative inspection in the report.
    per_example = [
        {
            "text": t,
            "true_labels": sorted(true_label_sets[i]),
            "predicted_labels": sorted(pred_label_sets[i]),
        }
        for i, t in enumerate(texts)
    ]

    save_json(report, f"{RESULTS_DIR}/issue_categorization_metrics.json")
    save_json(per_example, f"{RESULTS_DIR}/issue_categorization_predictions.json")

    return report


if __name__ == "__main__":
    main()
