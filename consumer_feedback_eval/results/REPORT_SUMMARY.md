# Model Evaluation Summary

## 1. Sentiment Classifier — tabularisai/multilingual-sentiment-analysis

Evaluated on 56 hand-labeled examples.

| Metric | Value |
|---|---|
| Macro-F1 | 0.7687 |
| Weighted-F1 | 0.7685 |
| Quadratic Weighted Kappa | 0.9082 |
| Mean Absolute Error (class index) | 0.2679 |

Confusion matrix and plot saved to `results/sentiment_confusion_matrix.png`.

## 2. Issue Categorization — cross-encoder/nli-deberta-v3-base (zero-shot)

Evaluated on 36 hand-labeled, multi-label examples.

| Metric | Value |
|---|---|
| Micro-F1 | 0.3784 |
| Macro-F1 | 0.3957 |
| Hamming Loss | 0.6389 |
| Jaccard Similarity (sample-averaged) | 0.2403 |
| Jaccard Similarity (macro-averaged) | 0.2520 |

**Per-label precision / recall / F1:**

| Label | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Bug / Software Defect | 0.222 | 1.000 | 0.364 | 8 |
| Hardware / Physical Defect | 0.212 | 1.000 | 0.350 | 7 |
| Shipping / Delivery Delay | 0.240 | 1.000 | 0.387 | 6 |
| Billing / Refund Dispute | 0.438 | 1.000 | 0.609 | 7 |
| Customer Service / Support Issue | 0.229 | 1.000 | 0.372 | 8 |
| Feature Request / Missing Functionality | 0.171 | 1.000 | 0.293 | 6 |

## 3. Summarization — HuggingFaceTB/SmolLM2-135M

| Metric | Precision | Recall | F-measure/F1 |
|---|---|---|---|
| ROUGE1 | 0.0313 | 0.0431 | 0.0357 |
| ROUGE2 | 0.0000 | 0.0000 | 0.0000 |
| ROUGEL | 0.0212 | 0.0302 | 0.0245 |
| BERTScore | 0.1422 | 0.1505 | 0.1462 |

Note: SmolLM2-135M here is the base (non-instruct) checkpoint, prompted as a plain completion model. See `eval_summarization.py` docstring for details.
