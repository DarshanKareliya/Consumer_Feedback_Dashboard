import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

export default function IssueChart({ data, onBarClick, currentFilter, onClearFilter}) {
  return (
    <div
      style={{
        padding: "1.5rem",
        background: "#fff",
        border: "1px solid #ddd",
        borderRadius: "10px",
      }}
    >
      <h2>Issues</h2>
      <p style={{ fontSize: "0.9rem", color: "#666" }}>
        Most frequently mentioned issues.
      </p>
      <div style={{ height: 400 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis
              type="category"
              dataKey="issue"
              width={120}
              tick={{ fontSize: 11 }}
            />
            <Tooltip />
            <Bar
              dataKey="count"
              fill="#6f42c1"
              onClick={(entry) => onBarClick("issue", entry.issue)}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Clear Filter Button */}
      {currentFilter && (
        <button
          onClick={onClearFilter}
          style={{
            marginTop: "1rem",
            padding: "0.5rem 1rem",
            cursor: "pointer",
            borderRadius: "4px",
            border: "1px solid #ccc",
            background: "#f8f9fa",
          }}
        >
          Clear Platform Filter ({currentFilter})
        </button>
      )}
    </div>
  );
}
