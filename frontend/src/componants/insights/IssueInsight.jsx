import React, { useMemo, useState } from "react";

const SENTIMENTS = [
  "Very Negative",
  "Negative",
  "Neutral",
  "Positive",
  "Very Positive",
];

const COLORS = {
  "Very Negative": "#dc3545",
  Negative: "#ffc107",
  Neutral: "#6c757d",
  Positive: "#0d6efd",
  "Very Positive": "#198754",
};

function IssueInsight({
  issue,
  comments,
  onClear,
  onViewComments,
  analysisId,
}) {
  const [review, setReview] = useState("");
  const [loadingReview, setLoadingReview] = useState(false);
  const [reviewError, setReviewError] = useState("");
  const issueComments = useMemo(() => {
    return comments.filter(
      (comment) =>
        Array.isArray(comment.issue_categories) &&
        comment.issue_categories.includes(issue),
    );
  }, [comments, issue]);

  const generateReview = async () => {
    if (!analysisId || !issue) {
      return;
    }

    setLoadingReview(true);
    setReviewError("");
    setReview("");

    try {
      const response = await fetch("/api/issue-insights", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          analysis_id: analysisId,
          issue_category: issue,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(errorData.detail || "Failed to generate review");
      }

      const data = await response.json();

      setReview(data.summary);
    } catch (error) {
      console.error("Review generation failed:", error);

      setReviewError(error.message || "Failed to generate review");
    } finally {
      setLoadingReview(false);
    }
  };

  // --------------------------------------------
  // SENTIMENT COUNTS
  // --------------------------------------------

  const sentimentCounts = {};

  SENTIMENTS.forEach((sentiment) => {
    sentimentCounts[sentiment] = 0;
  });

  issueComments.forEach((comment) => {
    if (sentimentCounts[comment.sentiment] !== undefined) {
      sentimentCounts[comment.sentiment]++;
    }
  });

  // --------------------------------------------
  // PLATFORM COUNTS
  // --------------------------------------------

  const platformCounts = {};

  issueComments.forEach((comment) => {
    const platform = comment.source || "Unknown";

    platformCounts[platform] = (platformCounts[platform] || 0) + 1;
  });

  const topPlatforms = Object.entries(platformCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  // --------------------------------------------
  // ACTION COUNTS
  // --------------------------------------------

  const actionCounts = {};

  issueComments.forEach((comment) => {
    if (Array.isArray(comment.actions)) {
      comment.actions.forEach((action) => {
        actionCounts[action] = (actionCounts[action] || 0) + 1;
      });
    }
  });

  const topActions = Object.entries(actionCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  // --------------------------------------------
  // OVERALL SENTIMENT
  // --------------------------------------------

  const positive =
    sentimentCounts["Positive"] + sentimentCounts["Very Positive"];

  const negative =
    sentimentCounts["Negative"] + sentimentCounts["Very Negative"];

  let overallSentiment = "Neutral";

  if (positive > negative) {
    overallSentiment = "Positive";
  } else if (negative > positive) {
    overallSentiment = "Negative";
  }

  return (
    <div>
      {/* Header */}

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "1.5rem",
        }}
      >
        <div>
          <h2 style={{ margin: 0 }}>🔎 {issue} Insights</h2>

          <p
            style={{
              margin: "0.4rem 0 0",
              color: "#666",
            }}
          >
            Detailed analysis of the {issue} issue.
          </p>
        </div>

        <button
          onClick={onClear}
          style={{
            padding: "0.5rem 1rem",
            border: "1px solid #ccc",
            background: "#fff",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          Clear
        </button>
      </div>

      {/* Summary */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, 1fr)",
          gap: "1rem",
          marginBottom: "1.5rem",
        }}
      >
        <div
          style={{
            padding: "1rem",
            background: "#f8f9fa",
            borderRadius: "8px",
          }}
        >
          <div style={{ color: "#666" }}>Issue Mentions</div>

          <strong style={{ fontSize: "1.5rem" }}>{issueComments.length}</strong>
        </div>

        <div
          style={{
            padding: "1rem",
            background: "#f8f9fa",
            borderRadius: "8px",
          }}
        >
          <div style={{ color: "#666" }}>Overall Sentiment</div>

          <strong
            style={{
              fontSize: "1.5rem",
              color: COLORS[overallSentiment] || "#333",
            }}
          >
            {overallSentiment}
          </strong>
        </div>
      </div>

      {/* Details */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr 1fr",
          gap: "2rem",
        }}
      >
        {/* Sentiment */}

        <div>
          <h3>Sentiment</h3>

          {SENTIMENTS.map((sentiment) => (
            <div
              key={sentiment}
              style={{
                display: "flex",
                justifyContent: "space-between",
                padding: "0.6rem 0",
                borderBottom: "1px solid #eee",
              }}
            >
              <span>{sentiment}</span>

              <strong>{sentimentCounts[sentiment]}</strong>
            </div>
          ))}
        </div>

        {/* Platforms */}

        <div>
          <h3>Platforms</h3>

          {topPlatforms.length === 0 ? (
            <p style={{ color: "#666" }}>No platform information available.</p>
          ) : (
            topPlatforms.map(([platform, count]) => (
              <div
                key={platform}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "0.6rem 0",
                  borderBottom: "1px solid #eee",
                }}
              >
                <span>{platform}</span>

                <strong>{count}</strong>
              </div>
            ))
          )}
        </div>

        {/* Actions */}

        <div>
          <h3>Related Actions</h3>

          {topActions.length === 0 ? (
            <p style={{ color: "#666" }}>No actions available.</p>
          ) : (
            topActions.map(([action, count]) => (
              <div
                key={action}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  gap: "1rem",
                  padding: "0.6rem 0",
                  borderBottom: "1px solid #eee",
                }}
              >
                <span>{action}</span>

                <strong>{count}</strong>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Comments */}

      {/* AI Review */}

      <div
        style={{
          marginBottom: "1.5rem",
          padding: "1.25rem",
          background: "#f8f9fa",
          borderRadius: "8px",
          border: "1px solid #e9ecef",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "0.75rem",
          }}
        >
          <div>
            <h3 style={{ margin: 0 }}>AI Review</h3>

            <p
              style={{
                margin: "0.3rem 0 0",
                color: "#666",
                fontSize: "0.9rem",
              }}
            >
              AI-generated insights from comments related to this issue.
            </p>
          </div>

          <button
            onClick={generateReview}
            disabled={loadingReview}
            style={{
              padding: "0.6rem 1rem",
              background: loadingReview ? "#aaa" : "#6f42c1",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
              cursor: loadingReview ? "not-allowed" : "pointer",
            }}
          >
            {loadingReview ? "Generating..." : "Generate Review"}
          </button>
        </div>

        {loadingReview && (
          <p style={{ color: "#666" }}>Analyzing comments with AI...</p>
        )}

        {reviewError && (
          <p
            style={{
              color: "#dc3545",
            }}
          >
            {reviewError}
          </p>
        )}

        {review && !loadingReview && (
          <div
            style={{
              padding: "1rem",
              background: "#fff",
              borderRadius: "6px",
              lineHeight: 1.6,
            }}
          >
            {review}
          </div>
        )}
      </div>

      <div style={{ marginTop: "1.5rem" }}>
        <button
          onClick={() => onViewComments(issueComments)}
          style={{
            padding: "0.7rem 1rem",
            background: "#6f42c1",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          View {issueComments.length} Related Comments
        </button>
      </div>
    </div>
  );
}

export default IssueInsight;
