import React from "react";

function ExportButtons({ data }) {
  const exportJSON = () => {
    if (!data) return;

    const jsonString = JSON.stringify(data, null, 2);

    const blob = new Blob([jsonString], {
      type: "application/json",
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = `${data.keyword || "dashboard"}-report.json`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  const exportCSV = () => {
    if (!data || !data.comments || data.comments.length === 0) {
      return;
    }

    const comments = data.comments;

    // Get all unique columns from the comments
    const columns = [
      "keyword",
      ...new Set(comments.flatMap((comment) => Object.keys(comment))),
    ];

    // Escape values so commas, quotes, and newlines don't break CSV
    const escapeCSV = (value) => {
      if (value === null || value === undefined) {
        return "";
      }

      const stringValue =
        typeof value === "object" ? JSON.stringify(value) : String(value);

      return `"${stringValue.replace(/"/g, '""')}"`;
    };

    // CSV header
    const header = columns.map(escapeCSV).join(",");

    // CSV rows
    const rows = comments.map((comment) =>
      columns
        .map((column) => {
          if (column === "keyword") {
            return escapeCSV(data.keyword);
          }

          return escapeCSV(comment[column]);
        })
        .join(","),
    );

    const csvContent = [header, ...rows].join("\n");

    const blob = new Blob([csvContent], {
      type: "text/csv;charset=utf-8;",
    });

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = `${data.keyword || "dashboard"}-comments.csv`;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  };

  return (
    <div
      style={{
        display: "flex",
        gap: "0.75rem",
        marginTop: "1rem",
        marginBottom: "2rem",
      }}
    >
      <button
        onClick={exportCSV}
        disabled={!data?.comments?.length}
        style={{
          padding: "0.6rem 1rem",
          border: "1px solid #198754",
          borderRadius: "6px",
          background: "#198754",
          color: "#fff",
          cursor: "pointer",
          fontWeight: "500",
        }}
      >
        📥 Export CSV
      </button>

      <button
        onClick={exportJSON}
        disabled={!data}
        style={{
          padding: "0.6rem 1rem",
          border: "1px solid #0d6efd",
          borderRadius: "6px",
          background: "#0d6efd",
          color: "#fff",
          cursor: "pointer",
          fontWeight: "500",
        }}
      >
        📥 Export JSON
      </button>
    </div>
  );
}

export default ExportButtons;
