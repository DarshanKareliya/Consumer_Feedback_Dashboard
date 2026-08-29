"""
Shared metric helpers for the three model evaluations.

Kept in one place so the three eval scripts (eval_sentiment.py,
eval_issue_categorization.py, eval_summarization.py) do not duplicate
metric math, and so the numbers reported in the project report are
computed the same way everywhere.
"""

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import (
    f1_score,
    cohen_kappa_score,
    mean_absolute_error,
    confusion_matrix,
    precision_recall_fscore_support,
    hamming_loss,
    jaccard_score,
)


# ---------------------------------------------------------------------------
# Single-label ordinal classification (used by the sentiment evaluation)
# ---------------------------------------------------------------------------

def ordinal_classification_report(y_true, y_pred, class_names):
    """
    y_true, y_pred: 1D int arrays/lists with class indices 0..K-1
    class_names: list of K human-readable class names, in index order
    Returns a dict with macro-F1, weighted-F1, quadratic weighted kappa,
    mean absolute error over the class index, and the confusion matrix.
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    labels = list(range(len(class_names)))

    macro_f1 = f1_score(y_true, y_pred, average="macro", labels=labels, zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average="weighted", labels=labels, zero_division=0)
    qwk = cohen_kappa_score(y_true, y_pred, weights="quadratic", labels=labels)
    mae = mean_absolute_error(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    return {
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "quadratic_weighted_kappa": float(qwk),
        "mean_absolute_error": float(mae),
        "confusion_matrix": cm.tolist(),
        "class_names": class_names,
        "n_examples": int(len(y_true)),
    }


def plot_confusion_matrix(cm, class_names, title, save_path):
    """Save a labeled confusion matrix heatmap as a PNG (no seaborn dependency)."""
    import matplotlib.pyplot as plt

    cm = np.asarray(cm)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names, rotation=45, ha="right")
    ax.set_yticklabels(class_names)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)

    thresh = cm.max() / 2 if cm.max() > 0 else 0.5
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j, i, str(cm[i, j]),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black",
            )

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Multi-label classification (used by the issue-categorization evaluation)
# ---------------------------------------------------------------------------

def multilabel_report(y_true_bin, y_pred_bin, label_names):
    """
    y_true_bin, y_pred_bin: 2D arrays of shape (n_examples, n_labels), values in {0,1}
    label_names: list of n_labels label names, in column order
    """
    y_true_bin = np.asarray(y_true_bin)
    y_pred_bin = np.asarray(y_pred_bin)

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true_bin, y_pred_bin, average=None, zero_division=0
    )

    per_label = []
    for i, name in enumerate(label_names):
        per_label.append({
            "label": name,
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        })

    micro_f1 = f1_score(y_true_bin, y_pred_bin, average="micro", zero_division=0)
    macro_f1 = f1_score(y_true_bin, y_pred_bin, average="macro", zero_division=0)
    h_loss = hamming_loss(y_true_bin, y_pred_bin)

    # Sample-averaged Jaccard: mean over examples of |intersection|/|union|,
    # with the sklearn convention that an all-zero true+pred row counts as 1.0.
    jaccard_samples = jaccard_score(y_true_bin, y_pred_bin, average="samples", zero_division=1)
    jaccard_macro = jaccard_score(y_true_bin, y_pred_bin, average="macro", zero_division=0)

    return {
        "per_label": per_label,
        "micro_f1": float(micro_f1),
        "macro_f1": float(macro_f1),
        "hamming_loss": float(h_loss),
        "jaccard_samples_avg": float(jaccard_samples),
        "jaccard_macro_avg": float(jaccard_macro),
        "n_examples": int(y_true_bin.shape[0]),
        "label_names": label_names,
    }


# ---------------------------------------------------------------------------
# Summarization metrics
# ---------------------------------------------------------------------------

def rouge_report(predictions, references):
    """
    Computes average ROUGE-1 / ROUGE-2 / ROUGE-L (precision, recall, f-measure)
    over a list of (prediction, reference) string pairs, using rouge-score.
    """
    from rouge_score import rouge_scorer

    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

    totals = {k: {"precision": 0.0, "recall": 0.0, "fmeasure": 0.0} for k in ["rouge1", "rouge2", "rougeL"]}
    per_example = []

    for pred, ref in zip(predictions, references):
        scores = scorer.score(ref, pred)
        row = {}
        for k in totals:
            totals[k]["precision"] += scores[k].precision
            totals[k]["recall"] += scores[k].recall
            totals[k]["fmeasure"] += scores[k].fmeasure
            row[k] = {
                "precision": scores[k].precision,
                "recall": scores[k].recall,
                "fmeasure": scores[k].fmeasure,
            }
        per_example.append(row)

    n = len(predictions)
    averages = {
        k: {metric: v / n for metric, v in totals[k].items()}
        for k in totals
    }
    return {"averages": averages, "per_example": per_example}


def bertscore_report(predictions, references, model_type="microsoft/deberta-base-mnli", lang="en"):
    """
    Computes BERTScore precision/recall/F1 for each (prediction, reference) pair
    and returns per-example scores plus corpus-level averages.

    model_type defaults to a mid-sized model to keep the download small; pass
    lang="en" and leave model_type=None to let bert-score pick its default
    (roberta-large) if you want the numbers most comparable to published results.
    """
    from bert_score import score as bertscore_score

    kwargs = {"lang": lang, "verbose": False}
    if model_type:
        kwargs = {"model_type": model_type, "verbose": False}

    P, R, F1 = bertscore_score(predictions, references, **kwargs)

    per_example = [
        {"precision": float(p), "recall": float(r), "f1": float(f)}
        for p, r, f in zip(P.tolist(), R.tolist(), F1.tolist())
    ]
    averages = {
        "precision": float(P.mean()),
        "recall": float(R.mean()),
        "f1": float(F1.mean()),
    }
    return {"averages": averages, "per_example": per_example}


# ---------------------------------------------------------------------------
# I/O helper
# ---------------------------------------------------------------------------

def save_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    print(f"Saved: {path}")
