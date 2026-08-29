import React, { useMemo } from "react";

const COLORS = {
  "Very Negative": "#dc3545",
  Negative: "#ffc107",
  Neutral: "#6c757d",
  Positive: "#0d6efd",
  "Very Positive": "#198754",
};

function SentimentInsight({
  sentiment,
  comments,
  onClear,
  onViewComments,
}) {
  const selectedComments = useMemo(() => {
    return comments.filter(
      (comment) => comment.sentiment === sentiment
    );
  }, [comments, sentiment]);

  const totalComments = comments.length;
  const selectedCount = selectedComments.length;

  const percentage =
    totalComments > 0
      ? ((selectedCount / totalComments) * 100).toFixed(1)
      : 0;

  // --------------------------------------------
  // ISSUE COUNTS
  // --------------------------------------------

  const issueCounts = {};

  selectedComments.forEach((comment) => {
    if (Array.isArray(comment.issue_categories)) {
      comment.issue_categories.forEach((issue) => {
        issueCounts[issue] = (issueCounts[issue] || 0) + 1;
      });
    }
  });

  const topIssues = Object.entries(issueCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  // --------------------------------------------
  // PLATFORM COUNTS
  // --------------------------------------------

  const platformCounts = {};

  selectedComments.forEach((comment) => {
    const platform = comment.source || "Unknown";

    platformCounts[platform] =
      (platformCounts[platform] || 0) + 1;
  });

  const topPlatforms = Object.entries(platformCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

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
            🔎 {sentiment} Sentiment Insights
          </h2>

          <p
            style={{
              margin: "0.4rem 0 0",
              color: "#666",
            }}
          >
            Detailed analysis of {sentiment.toLowerCase()} feedback.
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
          <div style={{ color: "#666", fontSize: "0.85rem" }}>
            Comments
          </div>

          <strong style={{ fontSize: "1.5rem" }}>
            {selectedCount}
          </strong>
        </div>

        <div
          style={{
            padding: "1rem",
            background: "#f8f9fa",
            borderRadius: "8px",
          }}
        >
          <div style={{ color: "#666", fontSize: "0.85rem" }}>
            Percentage of total
          </div>

          <strong
            style={{
              fontSize: "1.5rem",
              color: COLORS[sentiment] || "#333",
            }}
          >
            {percentage}%
          </strong>
        </div>
      </div>

      {/* Insights */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "2rem",
        }}
      >
        {/* Issues */}

        <div>
          <h3>What are people talking about?</h3>

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

        {/* Platforms */}

        <div>
          <h3>Where is this sentiment coming from?</h3>

          {topPlatforms.length === 0 ? (
            <p style={{ color: "#666" }}>
              No platform information available.
            </p>
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
      </div>

      {/* Comments */}

      <div style={{ marginTop: "1.5rem" }}>
        <button
          onClick={() => onViewComments(selectedComments)}
          style={{
            padding: "0.7rem 1rem",
            background: COLORS[sentiment] || "#333",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
          }}
        >
          View {selectedCount} Related Comments
        </button>
      </div>
    </div>
  );
}

export default SentimentInsight;