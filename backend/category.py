import json
from transformers import pipeline
import torch

# 1. Setup Device
device = 0 if torch.cuda.is_available() else (
    -1 if not torch.backends.mps.is_available() else "mps"
)

# 2. Load classifier
classifier = pipeline(
    "zero-shot-classification",
    model="/Users/darshankareliya/.cache/huggingface/hub/models--cross-encoder--nli-deberta-v3-base/snapshots/6c749ce3425cd33b46d187e45b92bbf96ee12ec7",
    device=device
)

ISSUE_CATEGORY_MAPPING = {
    "Software bug or application malfunction": "Bug / Software Defect",
    "Hardware defect or physical product problem": "Hardware / Physical Defect",
    "Shipping, delivery, or package tracking problem": "Shipping / Delivery Delay",
    "Billing, payment, refund, or pricing dispute": "Billing / Refund Dispute",
    "Customer service or technical support problem": "Customer Service / Support Issue",
    "Missing feature or requested functionality": "Feature Request / Missing Functionality"
}

ISSUE_CATEGORIES = list(ISSUE_CATEGORY_MAPPING.keys())


CATEGORY_ACTIONS = {
    "Bug / Software Defect": "create_software_bug",
    "Hardware / Physical Defect": "create_hardware_case",
    "Shipping / Delivery Delay": "contact_logistics",
    "Billing / Refund Dispute": "contact_billing",
    "Customer Service / Support Issue": "create_support_ticket",
    "Feature Request / Missing Functionality": "add_to_feature_backlog",
    "General Dissatisfaction": "manual_review"
}


def categorize_negative_feedback(
    feedback_items: list,
    threshold: float = 0.45,
    batch_size: int = 16
) -> list:

    if not feedback_items:
        return []

    # Extract all texts
    texts = [
        item.get("text", "")
        for item in feedback_items
    ]

    # Run inference in batches
    predictions = classifier(
        texts,
        candidate_labels=ISSUE_CATEGORIES,
        multi_label=True,
        batch_size=batch_size
    )

    enriched_results = []

    # Match each prediction to its original item
    for item, prediction in zip(feedback_items, predictions):

        # Model labels -> Business-friendly labels
        assigned_issues = [
            ISSUE_CATEGORY_MAPPING[label]
            for label, score in zip(
                prediction["labels"],
                prediction["scores"]
            )
            if score >= threshold
        ]

        # Fallback
        if not assigned_issues:
            assigned_issues = ["General Dissatisfaction"]


        # Use business-friendly labels for scores too
        issue_scores = {
            ISSUE_CATEGORY_MAPPING[label]: round(score, 3)
            for label, score in zip(
                prediction["labels"],
                prediction["scores"]
            )
            if score >= threshold
        }

        enriched_item = {
            **item,
            "is_negative": True,
            "sentiment_level": item.get("sentiment", "Neutral"),
            "issue_categories": assigned_issues,
            "issue_scores": issue_scores
        }

        enriched_results.append(enriched_item)

    return enriched_results

# Example Usage
# if __name__ == "__main__":
#     sample_data = [
#         {
#             "text": "The laptop screen flickers constantly and customer support refused to process my refund.",
#             "sentiment": "Very Negative",
#             "source": "YouTube"
#         },
#         {
#             "text": "Amazing build quality and battery life lasts two full days!",
#             "sentiment": "Very Positive",
#             "source": "Reddit"
#         },
#         {
#             "text": "Ordered 3 weeks ago, package still hasn't arrived and tracking is broken.",
#             "sentiment": "Negative",
#             "source": "Amazon"
#         }
#     ]

#     results = categorize_negative_feedback(sample_data, threshold=0.95)
#     print(json.dumps(results, indent=2))
