import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid } from "recharts";

export default function SentimentDistributionChart({ data, currentFilter, onBarClick, onClearFilter, colors }) {
  return (
    <div
      style={{
        padding: "1.5rem",
        background: "#fff",
        border: "1px solid #ddd",
        borderRadius: "10px",
      }}
    >
      <h2>Sentiment Distribution</h2>
      <p style={{ fontSize: "0.9rem", color: "#666" }}>Click a bar to filter comments.</p>
      <div style={{ height: 400 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="sentiment" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" onClick={(entry) => onBarClick("sentiment", entry.sentiment)}>
              {data.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={colors[entry.sentiment] || "#6c757d"}
                  opacity={!currentFilter || currentFilter === entry.sentiment ? 1 : 0.3}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      {currentFilter && (
        <button
          onClick={onClearFilter}
          style={{ marginTop: "1rem", padding: "0.5rem 1rem", cursor: "pointer" }}
        >
          Clear Sentiment Filter
        </button>
      )}
    </div>
  );
}