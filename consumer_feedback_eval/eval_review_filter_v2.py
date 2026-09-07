# Revised zero-shot classification evaluation for the review-vs-not-review filter.


from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support, accuracy_score
from transformers import pipeline
import torch

# =========================================================================
# 1. Dataset (same 100 samples, same expected labels as before)
# =========================================================================
try:
    from dataset_v3_labeled import EVALUATION_DATASET
    # EVALUATION_DATASET= YOUTUBE_DATA["text"]
except ImportError:
    raise ImportError(
        "Point this import at your existing EVALUATION_DATASET (the 100-sample "
        "list with 'text' and 'expected' keys) or paste it in directly."
    )



# =========================================================================
# 2. Model Pipeline Initialization
# =========================================================================
device = 0 if torch.cuda.is_available() else (-1 if not torch.backends.mps.is_available() else "mps")

print(f"Loading cross-encoder/nli-deberta-v3-base on device: {device}...")
classifier = pipeline(
    "zero-shot-classification",
    model="/Users/darshankareliya/.cache/huggingface/hub/models--MoritzLaurer--bge-m3-zeroshot-v2.0/snapshots/9abf1c8aaeb82a2447809c20753ed0b106b76652",
    device=device
)

# =========================================================================
# 3. Descriptive candidate labels (fix #1) and custom template (fix #3)
# =========================================================================
# These map back onto your original 4 ground-truth categories, but the label
# text given to the model is descriptive, not a bare noun phrase.
LABEL_DESCRIPTIONS = {
    "product review": "a comment sharing personal experience, opinion, or feedback about using a product",
    "question": "a question asking for information about a product or video",
    "general comment": "a general reaction or opinion about the video itself, not about a product",
    "spam": "a promotional, scam, or unrelated comment trying to advertise or solicit something",
}
CANDIDATE_LABELS = list(LABEL_DESCRIPTIONS.values())
LABEL_TEXT_TO_KEY = {v: k for k, v in LABEL_DESCRIPTIONS.items()}

TARGET_KEY = "product review"
TARGET_LABEL_TEXT = LABEL_DESCRIPTIONS[TARGET_KEY]

HYPOTHESIS_TEMPLATE = "This YouTube comment is {}."

THRESHOLDS = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60,
              0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.99]

# =========================================================================
# 4. Single-Pass Inference with multi_label=True (fix #2) and full score logging (fix #4)
# =========================================================================


def run_single_pass_inference(dataset, batch_size=16):
    texts = [item["text"] for item in dataset]
    ground_truth = [item["expected"] for item in dataset]

    print(f"\nRunning zero-shot inference over {len(texts)} samples (Batch size: {batch_size})...")

    raw_outputs = classifier(
        texts,
        candidate_labels=CANDIDATE_LABELS,
        hypothesis_template=HYPOTHESIS_TEMPLATE,
        multi_label=True,   # independent scoring per label, no softmax competition
        batch_size=batch_size
    )

    inference_cache = []
    for item, output, expected in zip(dataset, raw_outputs, ground_truth):
        # Build a dict of key -> score for every label, sorted by the model's own order
        label_scores = {
            LABEL_TEXT_TO_KEY[label]: score
            for label, score in zip(output["labels"], output["scores"])
        }

        top_key = max(label_scores, key=label_scores.get)
        top_score = label_scores[top_key]
        target_score = label_scores[TARGET_KEY]

        inference_cache.append({
            "text": item["text"],
            "expected_label": expected,
            "is_target_ground_truth": (expected == TARGET_KEY),
            "top_label": top_key,
            "top_score": top_score,
            "target_score": target_score,
            "all_scores": label_scores,  # full breakdown for diagnostics
        })

    return inference_cache


# =========================================================================
# 5. Threshold Sweep (against the target label's own score, not top_label)
# =========================================================================


def evaluate_binary_thresholds(cached_results, thresholds, target_key=TARGET_KEY):
    """
    Since multi_label=True gives each label an independent score, filtering
    should be based on target_score >= threshold directly, not on whether
    the target label happens to also be the top-scoring one.
    """
    y_true = [item["is_target_ground_truth"] for item in cached_results]
    sweep_results = []

    print("\n" + "=" * 80)
    print(f"BINARY CLASSIFICATION THRESHOLD SWEEP (Target: '{target_key}', independent score)")
    print("=" * 80)
    print(f"{'Threshold':<10} | {'Accuracy':<9} | {'Precision':<10} | {'Recall':<8} | {'F1-Score':<9} | {'TP':<4} {'FP':<4} {'FN':<4} {'TN':<4}")
    print("-" * 80)

    best_f1 = -1.0
    best_tau = None

    for tau in thresholds:
        y_pred = [item["target_score"] >= tau for item in cached_results]

        acc = accuracy_score(y_true, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, average="binary", zero_division=0
        )
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[False, True]).ravel()

        sweep_results.append({
            "threshold": tau, "accuracy": acc, "precision": prec,
            "recall": rec, "f1": f1, "confusion_matrix": (tp, fp, fn, tn)
        })

        if f1 > best_f1:
            best_f1 = f1
            best_tau = tau

        print(f"{tau:<10.2f} | {acc:<9.3f} | {prec:<10.3f} | {rec:<8.3f} | {f1:<9.3f} | {tp:<4} {fp:<4} {fn:<4} {tn:<4}")

    print("=" * 80)
    print(f"Optimal Threshold by F1-Score: {best_tau:.2f} (F1 = {best_f1:.3f})")

    return best_tau, sweep_results


def print_near_misses(cached_results, threshold, n=10):
    """
    Shows ground-truth product reviews that scored BELOW the threshold,
    ranked by how close they got. This tells you whether the model is
    missing reviews by a small margin (template/label issue, fixable)
    or by a large margin (deeper semantic mismatch).
    """
    misses = [
        item for item in cached_results
        if item["is_target_ground_truth"] and item["target_score"] < threshold
    ]
    misses.sort(key=lambda x: x["target_score"], reverse=True)

    print("\n" + "=" * 80)
    print(f"TOP {n} NEAR-MISS PRODUCT REVIEWS (highest target_score below threshold {threshold:.2f})")
    print("=" * 80)
    for item in misses[:n]:
        print(f"[{item['target_score']:.3f}] {item['text']}")
        print(f"    full scores: { {k: round(v,3) for k,v in item['all_scores'].items()} }")


def print_detailed_breakdown_at_threshold(cached_results, optimal_threshold, fallback_label="general comment"):
    y_true = [item["expected_label"] for item in cached_results]
    y_pred = []
    for item in cached_results:
        if item["target_score"] >= optimal_threshold:
            y_pred.append(TARGET_KEY)
        else:
            y_pred.append(fallback_label)

    print("\n" + "=" * 65)
    print(f"BINARY-FRAMED REPORT AT THRESHOLD {optimal_threshold:.2f} (Fallback: '{fallback_label}')")
    print("=" * 65)
    # Note: this report only distinguishes target vs fallback, since that is
    # what the filter actually needs. Use your existing multi-class script
    # if you also need question/spam breakdowns.
    print(classification_report(y_true, y_pred, digits=3, zero_division=0))


def extract_verified_reviews(cached_results, threshold, target_key=TARGET_KEY):
    return [
        {"text": item["text"], "confidence": round(item["target_score"], 3)}
        for item in cached_results
        if item["target_score"] >= threshold
    ]


# =========================================================================
# 6. Execution
# =========================================================================
if __name__ == "__main__":
    if not EVALUATION_DATASET:
        raise ValueError("EVALUATION_DATASET is empty. Please define or import your dataset.")

    results_cache = run_single_pass_inference(EVALUATION_DATASET, batch_size=16)

    best_threshold, sweep_data = evaluate_binary_thresholds(results_cache, THRESHOLDS)

    print_near_misses(results_cache, best_threshold, n=10)

    print_detailed_breakdown_at_threshold(results_cache, optimal_threshold=best_threshold)

    final_filtered_reviews = extract_verified_reviews(results_cache, threshold=best_threshold)

    print("\n" + "=" * 65)
    print(f"EXTRACTION COMPLETE: Found {len(final_filtered_reviews)} verified reviews.")
    print("=" * 65)

    for review in final_filtered_reviews[:3]:
        print(f"[{review['confidence']}] {review['text']}")
