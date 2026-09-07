import React from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";

export default function PlatformSentimentChart({ data, currentFilter, onClearFilter, onBarClick }) {
  return (
    <div
      style={{
        padding: "1.5rem",
        background: "#fff",
        border: "1px solid #ddd",
        borderRadius: "10px",
        marginBottom: "2rem",
      }}
    >
      <h2>Sentiment by Platform</h2>
      <p style={{ fontSize: "0.9rem", color: "#666" }}>
        See how positive, negative, and neutral sentiment is distributed across platforms.
      </p>
      
      <div style={{ height: 400 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="platform" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="Positive" fill="#198754" onClick={(entry) => onBarClick("platform", entry.platform)} />
            <Bar dataKey="Negative" fill="#dc3545" onClick={(entry) => onBarClick("platform", entry.platform)} />
            <Bar dataKey="Neutral" fill="#6c757d" onClick={(entry) => onBarClick("platform", entry.platform)} />
            <Bar dataKey="Very Positive" fill="#20c997" onClick={(entry) => onBarClick("platform", entry.platform)} />
            <Bar dataKey="Very Negative" fill="#842029" onClick={(entry) => onBarClick("platform", entry.platform)} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Clear Filter Button */}
      {currentFilter && (
        <button
          onClick={onClearFilter}
          style={{ marginTop: "1rem", padding: "0.5rem 1rem", cursor: "pointer", borderRadius: "4px", border: "1px solid #ccc", background: "#f8f9fa" }}
        >
          Clear Platform Filter ({currentFilter})
        </button>
      )}
    </div>
  );
}