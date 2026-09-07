import React from "react";

export default function CommentExplorer({ comments, filters, colors }) {
  return (
    <div
      style={{
        padding: "1.5rem",
        background: "#fff",
        border: "1px solid #ddd",
        borderRadius: "10px",
      }}
    >
      <h2>Comment Explorer</h2>
      
      {/* Active Filters Display */}
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1rem" }}>
        {filters.sentiment && (
          <span style={{ padding: "0.4rem 0.7rem", background: colors[filters.sentiment] || "#6c757d", color: "#fff", borderRadius: "20px", fontSize: "0.85rem" }}>
            Sentiment: {filters.sentiment}
          </span>
        )}
        {filters.platform && (
          <span style={{ padding: "0.4rem 0.7rem", background: "#343a40", color: "#fff", borderRadius: "20px", fontSize: "0.85rem" }}>
            Platform: {filters.platform}
          </span>
        )}
        {filters.issue && (
          <span style={{ padding: "0.4rem 0.7rem", background: "#6f42c1", color: "#fff", borderRadius: "20px", fontSize: "0.85rem" }}>
            Issue: {filters.issue}
          </span>
        )}
      </div>

      <p style={{ color: "#666" }}>Showing {comments.length} comments</p>

      <div style={{ maxHeight: "600px", overflowY: "auto", marginTop: "1rem" }}>
        {comments.map((comment, index) => (
          <div key={index} style={{ padding: "1rem", borderBottom: "1px solid #eee" }}>
            
            {/* Header: Sentiment & Source */}
            <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.75rem" }}>
              {comment.sentiment && (
                <span style={{ padding: "0.25rem 0.5rem", borderRadius: "4px", fontSize: "0.8rem", fontWeight: "bold", color: "#fff", backgroundColor: colors[comment.sentiment] || "#6c757d" }}>
                  {comment.sentiment}
                </span>
              )}
              {comment.source && (
                <span style={{ padding: "0.25rem 0.5rem", borderRadius: "4px", fontSize: "0.8rem", backgroundColor: "#e9ecef", color: "#333", fontWeight: "bold" }}>
                  {comment.source}
                </span>
              )}
            </div>

            {/* Core Comment Text */}
            <p style={{ fontSize: "1rem", color: "#333", margin: "0 0 1rem 0", lineHeight: "1.5" }}>
              {comment.text || comment.content || "No text provided."}
            </p>

            {/* AI Issue Tags */}
            {comment.issue_categories && comment.issue_categories.length > 0 && (
              <div>
                {comment.issue_categories.map((issue, idx) => (
                  <span key={idx} style={{ display: "inline-block", padding: "0.2rem 0.5rem", marginRight: "0.5rem", background: "#f8d7da", color: "#842029", borderRadius: "4px", fontSize: "0.75rem", border: "1px solid #f5c2c7" }}>
                    🏷️ {issue}
                  </span>
                ))}
              </div>
            )}
            
          </div>
        ))}
        {comments.length === 0 && <p style={{ color: "#666" }}>No comments found.</p>}
      </div>
    </div>
  );
}