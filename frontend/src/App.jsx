import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";

// Components
import SearchBar from "./componants/Searchbar";
import ExportButtons from "./componants/ExportButtons";
import InsightPanel from "./componants/insights/InsightPanel";
import KpiSection from "./componants/KpiSection";
import PlatformSentimentChart from "./componants/charts/PlatformSentimentChart";
import SentimentDistributionChart from "./componants/charts/SentimentDistributionChart";
import IssueChart from "./componants/charts/IssueChart";
import CommentExplorer from "./componants/CommentExplorer";

export const COLORS = {
  "Very Negative": "#dc3545",
  Negative: "#ffc107",
  Neutral: "#6c757d",
  Positive: "#0d6efd",
  "Very Positive": "#198754",
};

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    sentiment: null,
    platform: null,
    issue: null,
  });
  const [selectedInsight, setSelectedInsight] = useState(null);
  const [analysisId, setAnalysisId] = useState(null);

  const commentExplorerRef = useRef(null);

  const handleViewComments = () => {
    setSelectedInsight(null);
    commentExplorerRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const response = await axios.get("http://127.0.0.1:5000/api/dashboard");
      setData(response.data);
      setError(null);
    } catch (err) {
      setError("Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (searchQuery) => {
    if (!searchQuery) {
      setData(null);
      setSelectedInsight(null);
      setFilters({ sentiment: null, platform: null, issue: null });
      return;
    }

    setLoading(true);
    setError(null);
    setFilters({ sentiment: null, platform: null, issue: null });
    setSelectedInsight(null);

    try {
      const response = await axios.post("http://127.0.0.1:5000/api/analyze", {
        keyword: searchQuery,
      });
      setData(response.data);
      setAnalysisId(response.data.analysis_id);
    } catch (err) {
      setError(
        "Failed to fetch and analyze data. Make sure the backend is running.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleFilterClick = (type, value) => {
    setSelectedInsight({ type, value });
    setFilters((prev) => ({
      ...prev,
      [type]: prev[type] === value ? null : value,
    }));
  };

  if (loading)
    return (
      <div style={{ padding: "2rem" }}>
        <h2>Loading Dashboard Data...</h2>
      </div>
    );
  if (error)
    return (
      <div style={{ padding: "2rem" }}>
        <h2>Error</h2>
        <p>{error}</p>
      </div>
    );
  if (!data)
    return (
      <div style={{ padding: "2rem" }}>
        <h2>No dashboard data available.</h2>
      </div>
    );

  // Derive filtered comments
  const filteredComments = (data.comments || []).filter((comment) => {
    if (filters.sentiment && comment.sentiment !== filters.sentiment)
      return false;
    if (filters.platform && (comment.source || "Unknown") !== filters.platform)
      return false;
    if (
      filters.issue &&
      !(
        Array.isArray(comment.issue_categories) &&
        comment.issue_categories.includes(filters.issue)
      )
    )
      return false;
    return true;
  });

  // Derive platform sentiment chart data
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

  return (
    <div
      style={{
        padding: "2rem",
        fontFamily: "system-ui, sans-serif",
        background: "#f5f6f8",
        minHeight: "100vh",
      }}
    >
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ marginBottom: "0.5rem" }}>
          📊 AI Consumer Feedback Dashboard
        </h1>
        <p style={{ color: "#666", margin: 0 }}>
          Visualizing real-time sentiment analysis
        </p>
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

      <SearchBar onSearch={handleSearch} />
      {data && <ExportButtons data={data} />}

      <KpiSection kpis={data.kpis} />

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "2rem",
          marginBottom: "2rem",
        }}
      >
        <PlatformSentimentChart
          data={platformSentimentChartData}
          onBarClick={handleFilterClick}
          currentFilter={filters.platform}
          onClearFilter={() =>
            setFilters((prev) => ({ ...prev, platform: null }))
          }
        />
        <SentimentDistributionChart
          data={data.chart_data || []}
          currentFilter={filters.sentiment}
          onBarClick={handleFilterClick}
          onClearFilter={() =>
            setFilters((prev) => ({ ...prev, sentiment: null }))
          }
          colors={COLORS}
        />
        <IssueChart
          data={data.issue_chart_data || []}
          onBarClick={handleFilterClick}
          currentFilter={filters.issue}
          onClearFilter={() =>
            setFilters((prev) => ({ ...prev, issue: null }))
          }
        />
      </div>

      <InsightPanel
        insight={selectedInsight}
        comments={data.comments || []}
        analysisId={data.analysis_id}
        onClear={() => setSelectedInsight(null)}
        // onViewComments={(comments) =>
          // console.log("Related comments:", comments)
        // }
        onViewComments={handleViewComments}
      />

      <CommentExplorer
        ref={commentExplorerRef}
        comments={filteredComments}
        filters={filters}
        colors={COLORS}
      />
    </div>
  );
}

export default App;
