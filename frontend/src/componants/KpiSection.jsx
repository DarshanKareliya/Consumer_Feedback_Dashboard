import React from "react";

export default function KpiSection({ kpis }) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: "1rem",
        margin: "2rem 0",
      }}
    >
      <div
        style={{
          padding: "1.5rem",
          background: "#fff",
          borderRadius: "10px",
          border: "1px solid #ddd",
        }}
      >
        <h3 style={{ margin: 0, color: "#666" }}>Total Comments</h3>
        <p style={{ fontSize: "2rem", margin: "0.5rem 0 0", fontWeight: "bold" }}>
          {kpis?.total ?? 0}
        </p>
      </div>

      <div
        style={{
          padding: "1.5rem",
          background: "#fff",
          borderRadius: "10px",
          border: "1px solid #198754",
        }}
      >
        <h3 style={{ margin: 0, color: "#666" }}>Positive Sentiment</h3>
        <p style={{ fontSize: "2rem", margin: "0.5rem 0 0", fontWeight: "bold", color: "#198754" }}>
          {kpis?.positive_percent ?? 0}%
        </p>
      </div>

      <div
        style={{
          padding: "1.5rem",
          background: "#fff",
          borderRadius: "10px",
          border: "1px solid #dc3545",
        }}
      >
        <h3 style={{ margin: 0, color: "#666" }}>Negative Sentiment</h3>
        <p style={{ fontSize: "2rem", margin: "0.5rem 0 0", fontWeight: "bold", color: "#dc3545" }}>
          {kpis?.negative_percent ?? 0}%
        </p>
      </div>
    </div>
  );
}