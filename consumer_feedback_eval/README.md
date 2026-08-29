# Consumer Feedback Dashboard — Model Evaluation Suite

Evaluation code and hand-labeled gold data for the three models used in the
`Consumer_Feedback_Dashboard` project, to support the metrics section of the
project report.

| # | Task | Model | Script |
|---|---|---|---|
| 1 | Sentiment classification | `tabularisai/multilingual-sentiment-analysis` | `eval_sentiment.py` |
| 2 | Issue categorization (zero-shot, multi-label) | `cross-encoder/nli-deberta-v3-base` | `eval_issue_categorization.py` |
| 3 | Summarization | `HuggingFaceTB/SmolLM2-135M` | `eval_summarization.py` |

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

The first run of each script downloads its model from the Hugging Face Hub
(this needs internet access to `huggingface.co`), then caches it locally.

## Running the tests

Run everything and produce a report-ready markdown summary:

```bash
python run_all.py
```

Or run each evaluation independently:

```bash
python eval_sentiment.py
python eval_issue_categorization.py
python eval_summarization.py
```

## What gets produced

All outputs go to `results/`:

- `sentiment_metrics.json`, `sentiment_predictions.csv`, `sentiment_confusion_matrix.png`
- `issue_categorization_metrics.json`, `issue_categorization_predictions.json`
- `summarization_metrics.json`, `summarization_predictions.json`
- `REPORT_SUMMARY.md` — the combined markdown tables, ready to paste into the report

Console output also prints a readable summary (including the full 5x5
confusion matrix) as each script runs.

## Gold data

Since the repo itself has no labeled evaluation data, `data/` contains
hand-labeled gold sets built to look like the real Amazon/YouTube-scraped
feedback the dashboard processes:

- `sentiment_gold.csv` — 56 examples, balanced across the 5 classes (0=Very
  Negative … 4=Very Positive). Built by `make_sentiment_gold.py`.
- `issue_categorization_gold.json` — 36 examples labeled with 0, 1, or 2 of
  the 6 issue categories used in `backend/category.py`, so it evaluates the
  model as multi-label. Built by `make_issue_gold.py`.
- `summarization_gold.json` — 8 short comment batches, each with a
  human-written reference summary. Built by `make_summarization_gold.py`.

Feel free to extend these lists with real scraped comments before your final
run; more examples per class will make the metrics more stable and defensible
in the report. The `make_*_gold.py` scripts are left in `data/` purely as a
record of how the labels were constructed, not something you need to run.

## Notes for the report

- **Sentiment**: QWK and MAE are reported alongside macro/weighted-F1 because
  the classes are ordinal — a Positive predicted as Very Positive is a much
  smaller error than Positive predicted as Very Negative, and plain F1
  doesn't capture that. The confusion matrix plot is the clearest way to show
  where the model's errors cluster (usually adjacent classes, e.g. Positive
  vs. Neutral).
- **Issue categorization**: the model is used zero-shot with `multi_label=True`
  and a 0.45 score threshold, exactly matching `backend/category.py`. Hamming
  loss and Jaccard similarity are the standard pair of multi-label metrics —
  Hamming loss penalizes any individual wrong label, Jaccard rewards getting
  the whole label set right.
- **Summarization**: `HuggingFaceTB/SmolLM2-135M` is the base (non-instruct)
  checkpoint, so it's prompted as a plain completion model rather than
  through a chat template. The dashboard's actual code
  (`backend/summery_generator.py`) uses `SmolLM2-135M-Instruct` instead, so
  expect noticeably lower ROUGE/BERTScore here — that gap between base and
  instruct-tuned performance is itself worth a sentence in the report.
- `bertscore_report()` defaults to `microsoft/deberta-base-mnli` to keep the
  download small; pass `model_type=None` in `eval_summarization.py` if you
  want the (slower, larger) default `roberta-large` scorer for numbers most
  comparable to published BERTScore results.
