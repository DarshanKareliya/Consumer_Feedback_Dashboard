import React from "react";
import SentimentInsight from "./SentimentInsight";
import PlatformInsight from "./PlatformInsight";
import IssueInsight from "./IssueInsight";

function InsightPanel({ insight, comments, onClear, onViewComments, analysisId }) {
  if (!insight) {
    return null;
  }

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        backgroundColor: "rgba(0, 0, 0, 0.6)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 9999, // Ensures the modal sits above all charts
      }}
      onClick={onClear} // Clicking the dark background closes the modal
    >
      <div
        style={{
          padding: "2rem",
          background: "#fff",
          border: "1px solid #ddd",
          borderRadius: "12px",
          width: "90%",
          maxWidth: "800px",
          maxHeight: "85vh",
          overflowY: "auto",
          position: "relative",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
        }}
        onClick={(e) => e.stopPropagation()} // Prevents clicks inside the panel from closing it
      >
        <button
          onClick={onClear}
          style={{
            position: "absolute",
            top: "1rem",
            right: "1.5rem",
            background: "none",
            border: "none",
            fontSize: "1.5rem",
            cursor: "pointer",
            color: "#666",
          }}
        >
          &times;
        </button>

        {insight.type === "sentiment" && (
          <SentimentInsight
            sentiment={insight.value}
            comments={comments}
            onClear={onClear}
            onViewComments={onViewComments}
          />
        )}

        {insight.type === "platform" && (
          <PlatformInsight
            platform={insight.value}
            comments={comments}
            onClear={onClear}
            onViewComments={onViewComments}
          />
        )}

        {insight.type === "issue" && (
          <IssueInsight
            issue={insight.value}
            comments={comments}
            onClear={onClear}
            analysisId={analysisId}
            onViewComments={onViewComments}
          />
        )}
      </div>
    </div>
  );
}

export default InsightPanel;