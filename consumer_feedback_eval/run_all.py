"""
Runs all three model evaluations end to end and writes a single
markdown file (results/REPORT_SUMMARY.md) with tables you can paste
straight into the project report.

Run:
    python run_all.py
"""

from pathlib import Path

import eval_sentiment
import eval_issue_categorization
import eval_summarization

RESULTS_DIR = Path("results")


def build_markdown(sentiment_report, issue_report, rouge, bert):
    lines = []
    lines.append("# Model Evaluation Summary\n")

    lines.append("## 1. Sentiment Classifier — tabularisai/multilingual-sentiment-analysis\n")
    lines.append(f"Evaluated on {sentiment_report['n_examples']} hand-labeled examples.\n")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Macro-F1 | {sentiment_report['macro_f1']:.4f} |")
    lines.append(f"| Weighted-F1 | {sentiment_report['weighted_f1']:.4f} |")
    lines.append(f"| Quadratic Weighted Kappa | {sentiment_report['quadratic_weighted_kappa']:.4f} |")
    lines.append(f"| Mean Absolute Error (class index) | {sentiment_report['mean_absolute_error']:.4f} |")
    lines.append("\nConfusion matrix and plot saved to `results/sentiment_confusion_matrix.png`.\n")

    lines.append("## 2. Issue Categorization — cross-encoder/nli-deberta-v3-base (zero-shot)\n")
    lines.append(f"Evaluated on {issue_report['n_examples']} hand-labeled, multi-label examples.\n")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Micro-F1 | {issue_report['micro_f1']:.4f} |")
    lines.append(f"| Macro-F1 | {issue_report['macro_f1']:.4f} |")
    lines.append(f"| Hamming Loss | {issue_report['hamming_loss']:.4f} |")
    lines.append(f"| Jaccard Similarity (sample-averaged) | {issue_report['jaccard_samples_avg']:.4f} |")
    lines.append(f"| Jaccard Similarity (macro-averaged) | {issue_report['jaccard_macro_avg']:.4f} |")
    lines.append("\n**Per-label precision / recall / F1:**\n")
    lines.append("| Label | Precision | Recall | F1 | Support |")
    lines.append("|---|---|---|---|---|")
    for row in issue_report["per_label"]:
        lines.append(f"| {row['label']} | {row['precision']:.3f} | {row['recall']:.3f} | {row['f1']:.3f} | {row['support']} |")
    lines.append("")

    lines.append("## 3. Summarization — HuggingFaceTB/SmolLM2-135M\n")
    lines.append("| Metric | Precision | Recall | F-measure/F1 |")
    lines.append("|---|---|---|---|")
    for k in ["rouge1", "rouge2", "rougeL"]:
        avg = rouge["averages"][k]
        lines.append(f"| {k.upper()} | {avg['precision']:.4f} | {avg['recall']:.4f} | {avg['fmeasure']:.4f} |")
    b = bert["averages"]
    lines.append(f"| BERTScore | {b['precision']:.4f} | {b['recall']:.4f} | {b['f1']:.4f} |")
    lines.append(
        "\nNote: SmolLM2-135M here is the base (non-instruct) checkpoint, prompted as a "
        "plain completion model. See `eval_summarization.py` docstring for details.\n"
    )

    return "\n".join(lines)


def main():
    RESULTS_DIR.mkdir(exist_ok=True)

    print("\n### Running sentiment evaluation ###")
    sentiment_report = eval_sentiment.main()

    print("\n### Running issue categorization evaluation ###")
    issue_report = eval_issue_categorization.main()

    print("\n### Running summarization evaluation ###")
    rouge, bert = eval_summarization.main()

    markdown = build_markdown(sentiment_report, issue_report, rouge, bert)
    out_path = RESULTS_DIR / "REPORT_SUMMARY.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"\nAll done. Report-ready summary written to: {out_path}")


if __name__ == "__main__":
    main()
