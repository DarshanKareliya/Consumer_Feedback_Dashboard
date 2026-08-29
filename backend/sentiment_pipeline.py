from concurrent.futures import ThreadPoolExecutor, as_completed
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from youtube_search import YoutubeSearch
from itertools import islice
from youtube_comment_downloader import *
import json
import amazon
import youtube
import category
import logging

logging.basicConfig(level=logging.INFO)

log = logging.getLogger(__name__)


model_name = "/Users/darshankareliya/.cache/huggingface/hub/models--tabularisai--multilingual-sentiment-analysis/snapshots/5637087870c646575e013c27e8b0f7609576f433"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


def predict_sentiment(source_name, texts):

    inputs = tokenizer(texts, return_tensors="pt",
                       truncation=True, padding=True, max_length=512)

    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    sentiment_map = {0: "Very Negative", 1: "Negative",
                     2: "Neutral", 3: "Positive", 4: "Very Positive"}
    predicted_sentiments = [sentiment_map[p]
                            for p in torch.argmax(probabilities, dim=-1).tolist()]

    return predicted_sentiments


# call from flask
# predictions = predict_sentiment(comments_list)

# results = [
#     {
#         "text": text,
#         "sentiment": sentiment
#     }
#     for text, sentiment in zip(comments_list, predictions)
# ]


# with open("sentiment.json", "w", encoding="utf-8") as file:
#     json.dump(results, file, ensure_ascii=False, indent=4)

# ########################################################


# def process_reviews(source_name, reviews):
#     """Method C: This runs immediately as soon as ANY scraper finishes."""
#     print(f"\n[Method C] Processing results from: {source_name}")
#     print(f"Received {len(reviews)} items.")
#     # Add your logic here (e.g., sentiment analysis, saving to DB, summarization, etc.)
#     for review in reviews[:3]:  # Print first 3 for demo
#         print(f"  - {review[:100]}...")


def run_pipeline(product_name):
    # Map the scraper function to a human-readable source name
    tasks_map = {
        "YouTube": lambda: youtube.get_youtube_comments(product_name),
        "Amazon": lambda: amazon.get_amazon_reviews(product_name)
    }

    # 1. Create a dictionary to hold the final aggregated data
    final_aggregated_data = {}

    # Run both methods in parallel threads
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit tasks to the executor
        future_to_source = {
            executor.submit(func): source_name
            for source_name, func in tasks_map.items()
        }

        # as_completed yields tasks the MOMENT they finish
        for future in as_completed(future_to_source):
            source_name = future_to_source[future]
            try:
                result = future.result()  # This is your scraped text list

                # Check if result is a valid list of reviews
                if isinstance(result, list):
                    # Run inference
                    predictions = predict_sentiment(source_name, result)

                    
                    formatted_results = [
                        {
                            "text": text,
                            "sentiment": sentiment,
                            "source": source_name
                        }
                        for text, sentiment in zip(result, predictions)
                    ]

                    negative_items = [
                        item
                        for item in formatted_results
                        if item["sentiment"] in {"Negative", "Very Negative"}
                    ]

                    non_negative_items = [
                        item
                        for item in formatted_results
                        if item["sentiment"] not in {"Negative", "Very Negative"}
                    ]

                    categorized_negative_items = category.categorize_negative_feedback(
                        negative_items,
                        threshold=0.45
                    )

                    for item in non_negative_items:
                        item["is_negative"] = False
                        item["sentiment_level"] = None
                        item["issue_categories"] = []
                        item["issue_scores"] = {}
                        item["actions"] = []


                    for item in categorized_negative_items:
                        item["actions"] = [
                            category.CATEGORY_ACTIONS.get(
                                issue, "manual_review")
                            for issue in item["issue_categories"]
                        ]

                    
                    all_results = non_negative_items + categorized_negative_items

                    final_aggregated_data[source_name] = all_results
                    print(
                        f"[{source_name}] Successfully processed {len(formatted_results)} items.")

                else:
                    print(f"[{source_name}] Returned error/string: {result}")
                    final_aggregated_data[source_name] = {"error": str(result)}

            except Exception as exc:
                print(f"[{source_name}] Generated an exception: {exc}")
                final_aggregated_data[source_name] = {"error": str(exc)}

    # 2. Return the populated dictionary so Flask can send it to React
    return final_aggregated_data


# if __name__ == "__main__":
#     run_pipeline("Macbook air m5")
