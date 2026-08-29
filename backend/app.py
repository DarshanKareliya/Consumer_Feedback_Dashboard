import summery_generator
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import sentiment_pipeline
from analysis_storage import AnalysisStorage


app = Flask(__name__)

# FIX 1: Explicitly configure CORS to allow all origins on all /api/ routes
CORS(app)

storage = AnalysisStorage()


def load_data():
    file_path = "sentiment.json"
    if not os.path.exists(file_path):
        return pd.DataFrame(columns=["text", "sentiment"])

    df = pd.read_json(file_path)
    # Ensure categories are ordered logically
    sentiment_order = ["Very Negative", "Negative",
                       "Neutral", "Positive", "Very Positive"]
    df['sentiment'] = pd.Categorical(
        df['sentiment'], categories=sentiment_order, ordered=True)
    return df


@app.route('/api/generate-issue-review', methods=['POST'])
def generate_issue_review():

    try:

        # 1. Get request data

        req_data = request.get_json()

        if not req_data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400

        analysis_id = req_data.get("analysis_id")
        issue_category = req_data.get("issue_category")

        if not analysis_id:
            return jsonify({
                "success": False,
                "error": "analysis_id is required"
            }), 400

        if not issue_category:
            return jsonify({
                "success": False,
                "error": "issue_category is required"
            }), 400

        # 2. Load the specific analysis JSON

        analysis = storage.get(analysis_id)

        if analysis is None:
            return jsonify({
                "success": False,
                "error": "Analysis not found",
                "analysis_id": analysis_id
            }), 404

        # 3. Get comments for this issue

        issue_comments = storage.get_comments_by_issue(
            analysis_id=analysis_id,
            issue_category=issue_category
        )

        if not issue_comments:
            return jsonify({
                "success": False,
                "error": "No comments found for this issue",
                "analysis_id": analysis_id,
                "issue_category": issue_category,
                "comment_count": 0
            }), 404

        # 4. Generate AI review

        review_payload = {
            "keyword": analysis.get("keyword", ""),
            "kpis": analysis.get("kpis", {}),
            "chart_data": analysis.get("chart_data", []),
            "issue_chart_data": [
                entry for entry in analysis.get("issue_chart_data", [])
                if entry.get("issue") == issue_category
            ],
            "action_data": analysis.get("action_data", []),
            "comments": issue_comments
        }

        summary_result = summery_generator.summarize_feedback(review_payload)

        if summary_result["status"] == "error":
            return jsonify({
                "success": False,
                "error": "Failed to generate issue review",
                "details": summary_result.get("error")
            }), 500

        summary = summary_result["summary"]

        # -----------------------------------------
        # 5. Calculate some metadata
        # -----------------------------------------

        sentiment_counts = {
            "Very Negative": 0,
            "Negative": 0,
            "Neutral": 0,
            "Positive": 0,
            "Very Positive": 0
        }

        platform_counts = {}

        for comment in issue_comments:

            sentiment = comment.get("sentiment")

            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1

            platform = comment.get("source", "Unknown")

            platform_counts[platform] = (
                platform_counts.get(platform, 0) + 1
            )

        # -----------------------------------------
        # 6. Calculate overall sentiment
        # -----------------------------------------

        positive = (
            sentiment_counts["Positive"] +
            sentiment_counts["Very Positive"]
        )

        negative = (
            sentiment_counts["Negative"] +
            sentiment_counts["Very Negative"]
        )

        if positive > negative:
            overall_sentiment = "Positive"
        elif negative > positive:
            overall_sentiment = "Negative"
        else:
            overall_sentiment = "Neutral"

        # -----------------------------------------
        # 7. Return frontend-friendly response
        # -----------------------------------------

        return jsonify({
            "success": True,
            "analysis_id": analysis_id,
            "keyword": analysis.get("keyword", ""),

            "issue": {
                "category": issue_category,
                "comment_count": len(issue_comments),
                "overall_sentiment": overall_sentiment
            },

            "sentiment": {
                "counts": sentiment_counts,
                "positive": positive,
                "negative": negative
            },

            "platforms": [
                {"platform": platform, "count": count}
                for platform, count
                in sorted(platform_counts.items(), key=lambda x: x[1], reverse=True)
            ],

            "review": {
                "summary": summary
            }
        })

    except Exception as e:

        print(f"Error generating issue review: {e}")

        return jsonify({
            "success": False,
            "error": "Failed to generate issue review",
            "details": str(e)
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_product():
    req_data = request.get_json()
    keyword = req_data.get('keyword')
    # log.info(f'GOT THE REQUEST FOR ANALYZE, NAME: {keyword}')

    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    # 1. Run Inference (Returns a dictionary like {"YouTube": [...], "Amazon": [...]})
    predictions_dict = sentiment_pipeline.run_pipeline(keyword)

    # FIX 2: Flatten the dictionary into a single list of dictionaries
    flat_results = []
    for source, data in predictions_dict.items():
        if isinstance(data, list):
            flat_results.extend(data)

    if not flat_results:
        return jsonify({"error": "No comments found for this keyword."}), 404

    # 3. Format Data for the Dashboard using the flattened list
    df = pd.DataFrame(flat_results)

    sentiment_order = ["Very Negative", "Negative",
                       "Neutral", "Positive", "Very Positive"]
    df['sentiment'] = pd.Categorical(
        df['sentiment'], categories=sentiment_order, ordered=True)

    total_comments = len(df)
    positive = len(df[df['sentiment'].isin(['Positive', 'Very Positive'])])
    negative = len(df[df['sentiment'].isin(['Negative', 'Very Negative'])])
    sentiment_counts = df['sentiment'].value_counts().sort_index().to_dict()

    issue_counts = {}

    for categories in df["issue_categories"]:
        if isinstance(categories, list):
            for issue in categories:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

    issue_chart_data = [
        {
            "issue": issue,
            "count": count
        }
        for issue, count in issue_counts.items()
    ]

    action_counts = {}

    for actions in df["actions"]:
        if isinstance(actions, list):
            for action in actions:
                action_counts[action] = action_counts.get(action, 0) + 1

    response = {
        "keyword": keyword,
        "kpis": {
            "total": total_comments,
            "positive_percent": round((positive / total_comments) * 100, 1) if total_comments > 0 else 0,
            "negative_percent": round((negative / total_comments) * 100, 1) if total_comments > 0 else 0
        },
        "chart_data": [
            {
                "sentiment": k,
                "count": v
            }
            for k, v in sentiment_counts.items()
        ],

        "issue_chart_data": issue_chart_data,
        "action_data": [
            {
                "action": action,
                "count": count
            }
            for action, count in action_counts.items()
        ],
        "comments": df.to_dict(orient="records")
    }

    analysis_id = storage.save(response)

    print(analysis_id)

    response["analysis_id"] = analysis_id

    # 4. Return the JSON payload
    return jsonify(response)


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    df = load_data()

    if df.empty:
        return jsonify({"error": "Data not found. Run the inference script first."}), 404

    # Calculate High-Level KPIs
    total_comments = len(df)
    positive = len(df[df['sentiment'].isin(['Positive', 'Very Positive'])])
    negative = len(df[df['sentiment'].isin(['Negative', 'Very Negative'])])

    # Format Chart Data for React
    sentiment_counts = df['sentiment'].value_counts().sort_index().to_dict()
    chart_data = [{"sentiment": k, "count": v}
                  for k, v in sentiment_counts.items()]

    # Compile the JSON response
    response_data = {
        "kpis": {
            "total": total_comments,
            "positive_percent": round((positive / total_comments) * 100, 1) if total_comments > 0 else 0,
            "negative_percent": round((negative / total_comments) * 100, 1) if total_comments > 0 else 0
        },
        "chart_data": chart_data,
        "comments": df.to_dict(orient="records")
    }

    return jsonify(response_data)


if __name__ == '__main__':
    # Run the Flask app on port 5000
    app.run(debug=True, port=5000)
