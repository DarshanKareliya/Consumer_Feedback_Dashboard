import React from "react";
import SentimentInsight from "./SentimentInsight";
import PlatformInsight from "./PlatformInsight";
import IssueInsight from "./IssueInsight";

function InsightPanel({ insight, comments, onClear, onViewComments,analysisId }) {
  if (!insight) {
    return null;
  }

  return (
    <div
      style={{
        marginBottom: "2rem",
        padding: "1.5rem",
        background: "#fff",
        border: "1px solid #ddd",
        borderRadius: "10px",
      }}
    >
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
  );
}

export default InsightPanel;