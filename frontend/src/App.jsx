import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  CartesianGrid,
  Legend,
} from "recharts";
import "./App.css";
import SearchBar from "./componants/Searchbar";
import ExportButtons from "./componants/ExportButtons";
import InsightPanel from "./componants/insights/InsightPanel";

const COLORS = {
  "Very Negative": "#dc3545",
  Negative: "#ffc107",
  Neutral: "#6c757d",
  Positive: "#0d6efd",
  "Very Positive": "#198754",
};

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  // const [filter, setFilter] = useState("All");
  const [filters, setFilters] = useState({
    sentiment: null,
    platform: null,
    issue: null,
  });
  const [error, setError] = useState(null);
  const [selectedInsight, setSelectedInsight] = useState(null);
  const [analysisId, setAnalysisId] = useState(null);

  // --------------------------------------------------
  // GET DEFAULT DASHBOARD DATA
  // --------------------------------------------------
  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);

      const response = await axios.get("http://127.0.0.1:5000/api/dashboard");

      console.log("Dashboard response:", response.data);

      setData(response.data);
      setError(null);
    } catch (err) {
      console.error("Error fetching dashboard:", err);
      setError("Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // SEARCH / ANALYZE
  // --------------------------------------------------
  const handleSearch = async (searchQuery) => {
    if (!searchQuery) {
      setData(null);
      setSelectedInsight(null);
      setFilters({
        sentiment: null,
        platform: null,
        issue: null,
      });
      return;
    }

    setLoading(true);
    setError(null);
    setFilters({
      sentiment: null,
      platform: null,
      issue: null,
    });

    setSelectedInsight(null);

    try {
      const response = await axios.post("http://127.0.0.1:5000/api/analyze", {
        keyword: searchQuery,
      });

      console.log("Analysis response:", response.data);

      setData(response.data);
      setAnalysisId(response.data.analysis_id);
    } catch (err) {
      console.error("Error analyzing feedback:", err);

      setError(
        "Failed to fetch and analyze data. Make sure the backend is running.",
      );
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // LOADING
  // --------------------------------------------------
  if (loading) {
    return (
      <div style={{ padding: "2rem" }}>
        <h2>Loading Dashboard Data...</h2>
      </div>
    );
  }

  // --------------------------------------------------
  // ERROR
  // --------------------------------------------------
  if (error) {
    return (
      <div style={{ padding: "2rem" }}>
        <h2>Error</h2>
        <p>{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ padding: "2rem" }}>
        <h2>No dashboard data available.</h2>
      </div>
    );
  }

  // --------------------------------------------------
  // FILTER COMMENTS
  // --------------------------------------------------
  const filteredComments = (data.comments || []).filter((comment) => {
    // Sentiment filter
    if (filters.sentiment && comment.sentiment !== filters.sentiment) {
      return false;
    }

    // Platform filter
    if (
      filters.platform &&
      (comment.source || "Unknown") !== filters.platform
    ) {
      return false;
    }

    // Issue filter
    if (
      filters.issue &&
      !(
        Array.isArray(comment.issue_categories) &&
        comment.issue_categories.includes(filters.issue)
      )
    ) {
      return false;
    }

    return true;
  });

  const platformSentimentData = {};

  (data.comments || []).forEach((comment) => {
    const platform = comment.source || "Unknown";
    const sentiment = comment.sentiment || "Unknown";

    if (!platformSentimentData[platform]) {
      platformSentimentData[platform] = {
        platform,
        Positive: 0,
        Negative: 0,
        Neutral: 0,
        "Very Positive": 0,
        "Very Negative": 0,
      };
    }

    if (platformSentimentData[platform][sentiment] !== undefined) {
      platformSentimentData[platform][sentiment]++;
    }
  });

  const platformSentimentChartData = Object.values(platformSentimentData);

  // --------------------------------------------------
  // RENDER
  // --------------------------------------------------
  return (
    <div
      style={{
        padding: "2rem",
        fontFamily: "system-ui, sans-serif",
        background: "#f5f6f8",
        minHeight: "100vh",
      }}
    >
      {/* ==================================================
          HEADER
      ================================================== */}
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ marginBottom: "0.5rem" }}>
          📊 AI Consumer Feedback Dashboard
        </h1>

        <p style={{ color: "#666", margin: 0 }}>
          Visualizing real-time sentiment analysis
        </p>

        {/* Keyword from backend */}
        {data.keyword && (
          <div
            style={{
              display: "inline-block",
              marginTop: "1rem",
              padding: "0.5rem 1rem",
              background: "#e9ecef",
              borderRadius: "20px",
              fontWeight: "bold",
            }}
          >
            🔍 Keyword: {data.keyword}
          </div>
        )}
      </div>

      {/* ==================================================
          SEARCH
      ================================================== */}
      <SearchBar onSearch={handleSearch} />

      {data && <ExportButtons data={data} />}
      {/* ==================================================
          KPI SECTION
      ================================================== */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: "1rem",
          margin: "2rem 0",
        }}
      >
        {/* Total */}
        <div
          style={{
            padding: "1.5rem",
            background: "#fff",
            borderRadius: "10px",
            border: "1px solid #ddd",
          }}
        >
          <h3 style={{ margin: 0, color: "#666" }}>Total Comments</h3>

          <p
            style={{
              fontSize: "2rem",
              margin: "0.5rem 0 0",
              fontWeight: "bold",
            }}
          >
            {data.kpis?.total ?? 0}
          </p>
        </div>

        {/* Positive */}
        <div
          style={{
            padding: "1.5rem",
            background: "#fff",
            borderRadius: "10px",
            border: "1px solid #198754",
          }}
        >
          <h3 style={{ margin: 0, color: "#666" }}>Positive Sentiment</h3>

          <p
            style={{
              fontSize: "2rem",
              margin: "0.5rem 0 0",
              fontWeight: "bold",
              color: "#198754",
            }}
          >
            {data.kpis?.positive_percent ?? 0}%
          </p>
        </div>

        {/* Negative */}
        <div
          style={{
            padding: "1.5rem",
            background: "#fff",
            borderRadius: "10px",
            border: "1px solid #dc3545",
          }}
        >
          <h3 style={{ margin: 0, color: "#666" }}>Negative Sentiment</h3>

          <p
            style={{
              fontSize: "2rem",
              margin: "0.5rem 0 0",
              fontWeight: "bold",
              color: "#dc3545",
            }}
          >
            {data.kpis?.negative_percent ?? 0}%
          </p>
        </div>
      </div>

      {/* ==================================================
          SENTIMENT + ISSUE CHARTS
      ================================================== */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "2rem",
          marginBottom: "2rem",
        }}
      >
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
            See how positive, negative, and neutral sentiment is distributed
            across platforms.
          </p>

          <div style={{ height: 400 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={platformSentimentChartData}>
                <CartesianGrid strokeDasharray="3 3" />

                <XAxis dataKey="platform" />

                <YAxis />

                <Tooltip />

                <Legend />

                <Bar
                  dataKey="Positive"
                  fill="#198754"
                  name="Positive"
                  onClick={(entry) => {
                    const platform = entry.platform;

                    setSelectedInsight({
                      type: "platform",
                      value: platform,
                    });

                    setFilters((prev) => ({
                      ...prev,
                      platform: prev.platform === platform ? null : platform,
                    }));
                  }}
                />

                <Bar
                  dataKey="Negative"
                  fill="#dc3545"
                  name="Negative"
                  onClick={(entry) => {
                    const platform = entry.platform;

                    setSelectedInsight({
                      type: "platform",
                      value: platform,
                    });

                    setFilters((prev) => ({
                      ...prev,
                      platform: prev.platform === platform ? null : platform,
                    }));
                  }}
                />

                <Bar
                  dataKey="Neutral"
                  fill="#6c757d"
                  name="Neutral"
                  onClick={(entry) => {
                    const platform = entry.platform;

                    setSelectedInsight({
                      type: "platform",
                      value: platform,
                    });

                    setFilters((prev) => ({
                      ...prev,
                      platform: prev.platform === platform ? null : platform,
                    }));
                  }}
                />

                <Bar
                  dataKey="Very Positive"
                  fill="#20c997"
                  name="Very Positive"
                  onClick={(entry) => {
                    const platform = entry.platform;

                    setSelectedInsight({
                      type: "platform",
                      value: platform,
                    });

                    setFilters((prev) => ({
                      ...prev,
                      platform: prev.platform === platform ? null : platform,
                    }));
                  }}
                />

                <Bar
                  dataKey="Very Negative"
                  fill="#842029"
                  name="Very Negative"
                  onClick={(entry) => {
                    const platform = entry.platform;

                    setSelectedInsight({
                      type: "platform",
                      value: platform,
                    });

                    setFilters((prev) => ({
                      ...prev,
                      platform: prev.platform === platform ? null : platform,
                    }));
                  }}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        {/* ----------------------------------------------
            SENTIMENT CHART
        ---------------------------------------------- */}
        <div
          style={{
            padding: "1.5rem",
            background: "#fff",
            border: "1px solid #ddd",
            borderRadius: "10px",
          }}
        >
          <h2>Sentiment Distribution</h2>

          <p style={{ fontSize: "0.9rem", color: "#666" }}>
            Click a bar to filter comments.
          </p>

          <div style={{ height: 350 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.chart_data || []}>
                <CartesianGrid strokeDasharray="3 3" />

                <XAxis dataKey="sentiment" />

                <YAxis />

                <Tooltip />

                <Bar
                  dataKey="count"
                  onClick={(entry) => {
                    const sentiment = entry.sentiment;

                    setSelectedInsight({
                      type: "sentiment",
                      value: sentiment,
                    });

                    setFilters((prev) => ({
                      ...prev,
                      sentiment:
                        prev.sentiment === sentiment ? null : sentiment,
                    }));
                  }}
                >
                  {(data.chart_data || []).map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[entry.sentiment] || "#6c757d"}
                      opacity={
                        !filters.sentiment ||
                        filters.sentiment === entry.sentiment
                          ? 1
                          : 0.3
                      }
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {filters.sentiment && (
            <button
              onClick={() =>
                setFilters((prev) => ({
                  ...prev,
                  sentiment: null,
                }))
              }
              style={{
                marginTop: "1rem",
                padding: "0.5rem 1rem",
                cursor: "pointer",
              }}
            >
              Clear Sentiment Filter
            </button>
          )}
        </div>

        {/* ----------------------------------------------
            ISSUE CHART
        ---------------------------------------------- */}
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

          <div style={{ height: 350 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.issue_chart_data || []} layout="vertical">
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
                  onClick={(entry) => {
                    const issue = entry.issue;

                    setSelectedInsight({
                      type: "issue",
                      value: issue,
                    });

                    setFilters((prev) => ({
                      ...prev,
                      issue: prev.issue === issue ? null : issue,
                    }));
                  }}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* ==================================================
          ACTION CHART
      ================================================== */}
      {/* <div
        style={{
          padding: "1.5rem",
          background: "#fff",
          border: "1px solid #ddd",
          borderRadius: "10px",
          marginBottom: "2rem",
        }}
      >
        <h2>Recommended Actions</h2>

        <p style={{ fontSize: "0.9rem", color: "#666" }}>
          Actions identified from customer feedback.
        </p>

        <div style={{ height: 350 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.action_data || []}>
              <CartesianGrid strokeDasharray="3 3" />

              <XAxis
                dataKey="action"
                angle={-25}
                textAnchor="end"
                height={100}
              />

              <YAxis />

              <Tooltip />

              <Bar dataKey="count" fill="#fd7e14" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div> */}

      {/* ==================================================
    INTERACTIVE INSIGHTS
================================================== */}

      <InsightPanel
        insight={selectedInsight}
        comments={data.comments || []}
        analysisId={data.analysisId}
        onClear={() => setSelectedInsight(null)}
        onViewComments={(comments) => {
          console.log("Related comments:", comments);
        }}
      />

      {/* ==================================================
          COMMENT EXPLORER
      ================================================== */}
      <div
        style={{
          padding: "1.5rem",
          background: "#fff",
          border: "1px solid #ddd",
          borderRadius: "10px",
        }}
      >
        <h2>Comment Explorer </h2>
        <div
          style={{
            display: "flex",
            gap: "0.5rem",
            flexWrap: "wrap",
            marginBottom: "1rem",
          }}
        >
          {filters.sentiment && (
            <span
              style={{
                padding: "0.4rem 0.7rem",
                background: COLORS[filters.sentiment] || "#6c757d",
                color: "#fff",
                borderRadius: "20px",
                fontSize: "0.85rem",
              }}
            >
              Sentiment: {filters.sentiment}
            </span>
          )}

          {filters.platform && (
            <span
              style={{
                padding: "0.4rem 0.7rem",
                background: "#343a40",
                color: "#fff",
                borderRadius: "20px",
                fontSize: "0.85rem",
              }}
            >
              Platform: {filters.platform}
            </span>
          )}

          {filters.issue && (
            <span
              style={{
                padding: "0.4rem 0.7rem",
                background: "#6f42c1",
                color: "#fff",
                borderRadius: "20px",
                fontSize: "0.85rem",
              }}
            >
              Issue: {filters.issue}
            </span>
          )}
        </div>

        <p style={{ color: "#666" }}>
          Showing {filteredComments.length} comments
        </p>

        <div
          style={{
            maxHeight: "600px",
            overflowY: "auto",
            marginTop: "1rem",
          }}
        >
          {filteredComments.map((comment, index) => (
            <div
              key={index}
              style={{
                padding: "1rem",
                borderBottom: "1px solid #eee",
              }}
            >
              {/* SENTIMENT */}
              {comment.sentiment && (
                <span
                  style={{
                    display: "inline-block",
                    padding: "0.25rem 0.5rem",
                    borderRadius: "4px",
                    fontSize: "0.8rem",
                    fontWeight: "bold",
                    color: "#fff",
                    backgroundColor: COLORS[comment.sentiment] || "#6c757d",
                    marginBottom: "0.75rem",
                  }}
                >
                  {comment.sentiment}
                </span>
              )}

              {/* ALL COMMENT FIELDS */}
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, 1fr)",
                  gap: "0.75rem",
                }}
              >
                {Object.entries(comment).map(([key, value]) => (
                  <div key={key}>
                    <strong
                      style={{
                        display: "block",
                        color: "#555",
                        fontSize: "0.8rem",
                        marginBottom: "0.2rem",
                      }}
                    >
                      {key}
                    </strong>

                    <div
                      style={{
                        fontSize: "0.9rem",
                        wordBreak: "break-word",
                      }}
                    >
                      {value === null || value === undefined
                        ? "-"
                        : typeof value === "object"
                          ? JSON.stringify(value)
                          : String(value)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {filteredComments.length === 0 && (
            <p style={{ color: "#666" }}>No comments found.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
