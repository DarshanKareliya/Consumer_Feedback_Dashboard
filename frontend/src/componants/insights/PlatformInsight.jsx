import React, { useMemo } from "react";

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

function PlatformInsight({
  platform,
  comments,
  onClear,
  onViewComments,
}) {
  const platformComments = useMemo(() => {
    return comments.filter(
      (comment) => (comment.source || "Unknown") === platform
    );
  }, [comments, platform]);

  // --------------------------------------------
  // SENTIMENT COUNTS
  // --------------------------------------------

  const sentimentCounts = {};

  SENTIMENTS.forEach((sentiment) => {
    sentimentCounts[sentiment] = 0;
  });

  platformComments.forEach((comment) => {
    if (sentimentCounts[comment.sentiment] !== undefined) {
      sentimentCounts[comment.sentiment]++;
    }
  });

  // --------------------------------------------
  // ISSUE COUNTS
  // --------------------------------------------

  const issueCounts = {};

  platformComments.forEach((comment) => {
    if (Array.isArray(comment.issue_categories)) {
      comment.issue_categories.forEach((issue) => {
        issueCounts[issue] =
          (issueCounts[issue] || 0) + 1;
      });
    }
  });

  const topIssues = Object.entries(issueCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  // --------------------------------------------
  // OVERALL SENTIMENT
  // --------------------------------------------

  const positive =
    (sentimentCounts["Positive"] || 0) +
    (sentimentCounts["Very Positive"] || 0);

  const negative =
    (sentimentCounts["Negative"] || 0) +
    (sentimentCounts["Very Negative"] || 0);

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
          <h2 style={{ margin: 0 }}>
            🔎 {platform} Insights
          </h2>

          <p
            style={{
              margin: "0.4rem 0 0",
              color: "#666",
            }}
          >
            Sentiment and issue analysis for {platform}.
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
          <div style={{ color: "#666" }}>
            Total Comments
          </div>

          <strong style={{ fontSize: "1.5rem" }}>
            {platformComments.length}
          </strong>
        </div>

        <div
          style={{
            padding: "1rem",
            background: "#f8f9fa",
            borderRadius: "8px",
          }}
        >
          <div style={{ color: "#666" }}>
            Overall Sentiment
          </div>

          <strong
            style={{
              fontSize: "1.5rem",
              color:
                COLORS[overallSentiment] || "#333",
            }}
          >
            {overallSentiment}
          </strong>
        </div>
      </div>

      {/* Two columns */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "2rem",
        }}
      >
        {/* Sentiment */}

        <div>
          <h3>Sentiment Breakdown</h3>

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

              <strong>
                {sentimentCounts[sentiment]}
              </strong>
            </div>
          ))}
        </div>

        {/* Issues */}

        <div>
          <h3>Top Issues</h3>

          {topIssues.length === 0 ? (
            <p style={{ color: "#666" }}>
              No issue categories available.
            </p>
          ) : (
            topIssues.map(([issue, count]) => (
              <div
                key={issue}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "0.6rem 0",
                  borderBottom: "1px solid #eee",
                }}
              >
                <span>{issue}</span>

                <strong>{count}</strong>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Comments */}

      <div style={{ marginTop: "1.5rem" }}>
        <button
          onClick={() => onViewComments(platformComments)}
          style={{
            padding: "0.7rem 1rem",
            background: "#343a40",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          View {platformComments.length} Related Comments
        </button>
      </div>
    </div>
  );
}

export default PlatformInsight;