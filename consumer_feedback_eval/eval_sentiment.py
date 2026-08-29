"""
Evaluation for Model 1: tabularisai/multilingual-sentiment-analysis

Metrics reported:
  - Macro-F1 and Weighted-F1 across the 5 sentiment classes
  - Quadratic Weighted Kappa (QWK) and Mean Absolute Error (MAE) over the
    class index 0..4, treating sentiment as ordinal
  - Full 5x5 confusion matrix (printed, saved as CSV, and plotted as PNG)

Run:
    python eval_sentiment.py
"""

import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from metrics_utils import ordinal_classification_report, plot_confusion_matrix, save_json

MODEL_NAME = "/Users/darshankareliya/.cache/huggingface/hub/models--tabularisai--multilingual-sentiment-analysis/snapshots/5637087870c646575e013c27e8b0f7609576f433"
GOLD_CSV = "data/sentiment_gold.csv"
RESULTS_DIR = "results"

# Index order must match the model's label output (index 0..4).
CLASS_NAMES = ["Very Negative", "Negative", "Neutral", "Positive", "Very Positive"]
BATCH_SIZE = 16


def load_model():
    print(f"Loading model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    model.eval()
    return tokenizer, model


def predict_batch(texts, tokenizer, model):
    inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    return torch.argmax(probs, dim=-1).tolist()


def run_predictions(df, tokenizer, model):
    preds = []
    texts = df["text"].tolist()
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        preds.extend(predict_batch(batch, tokenizer, model))
    return preds


def print_report(report):
    print("\n" + "=" * 60)
    print("SENTIMENT CLASSIFIER — tabularisai/multilingual-sentiment-analysis")
    print("=" * 60)
    print(f"Examples evaluated : {report['n_examples']}")
    print(f"Macro-F1           : {report['macro_f1']:.4f}")
    print(f"Weighted-F1        : {report['weighted_f1']:.4f}")
    print(f"Quadratic W. Kappa : {report['quadratic_weighted_kappa']:.4f}")
    print(f"Mean Absolute Error: {report['mean_absolute_error']:.4f}")
    print("\nConfusion matrix (rows = true, cols = predicted):")
    header = "".ljust(16) + "".join(n[:10].rjust(12) for n in CLASS_NAMES)
    print(header)
    for i, row in enumerate(report["confusion_matrix"]):
        print(CLASS_NAMES[i].ljust(16) + "".join(str(v).rjust(12) for v in row))
    print("=" * 60)


def main():
    df = pd.read_csv(GOLD_CSV)
    assert set(df["label"].unique()) <= set(range(len(CLASS_NAMES))), \
        "Gold labels must be integers 0..4 matching CLASS_NAMES order"

    tokenizer, model = load_model()
    df["predicted_label"] = run_predictions(df, tokenizer, model)
    df["predicted_class"] = df["predicted_label"].map(lambda i: CLASS_NAMES[i])
    df["true_class"] = df["label"].map(lambda i: CLASS_NAMES[i])

    report = ordinal_classification_report(
        y_true=df["label"].tolist(),
        y_pred=df["predicted_label"].tolist(),
        class_names=CLASS_NAMES,
    )
    print_report(report)

    save_json(report, f"{RESULTS_DIR}/sentiment_metrics.json")
    df.to_csv(f"{RESULTS_DIR}/sentiment_predictions.csv", index=False)
    plot_confusion_matrix(
        report["confusion_matrix"], CLASS_NAMES,
        title="Sentiment Classifier — Confusion Matrix",
        save_path=f"{RESULTS_DIR}/sentiment_confusion_matrix.png",
    )
    print(f"Saved: {RESULTS_DIR}/sentiment_predictions.csv")
    print(f"Saved: {RESULTS_DIR}/sentiment_confusion_matrix.png")

    return report


if __name__ == "__main__":
    main()
