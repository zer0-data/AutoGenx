// result.jsx
import React, { useEffect, useState } from "react";
import { useLocation, Link } from "react-router-dom";

export default function Result() {
  const { state } = useLocation(); // data from navigate("/result", { state: data })
  const [files, setFiles] = useState({});
  const result = state || {};

  useEffect(() => {
    const fetchFiles = async () => {
      if (!result.project_path) return;
      const q = new URLSearchParams({ path: result.project_path });
      const res = await fetch(`/api/files?${q.toString()}`);
      const data = await res.json();
      setFiles(data.files || {});
    };
    fetchFiles();
  }, [result.project_path]);

  return (
    <div className="wrap">
      <h1>Project Generated</h1>

      <div className="card">
        <h3>Deployment Info</h3>
        <div className="info-grid">
          <div className="info-item">
            <div className="info-label">Preview</div>
            <div className="info-value">
              {result.preview_url ? (
                <a href={result.preview_url} target="_blank" rel="noreferrer">
                  Open local preview
                </a>
              ) : (
                "—"
              )}
            </div>
          </div>

          <div className="info-item">
            <div className="info-label">Download</div>
            <div className="info-value">
              {result.download_url ? (
                <a href={result.download_url}>Download ZIP</a>
              ) : (
                "—"
              )}
            </div>
          </div>

          <div className="info-item">
            <div className="info-label">GitHub Repo</div>
            <div className="info-value">
              {result.github_url ? (
                <a href={result.github_url} target="_blank" rel="noreferrer">
                  {result.github_url}
                </a>
              ) : (
                "—"
              )}
            </div>
          </div>

          <div className="info-item">
            <div className="info-label">Pages URL</div>
            <div className="info-value">
              {result.pages_url ? (
                <a href={result.pages_url} target="_blank" rel="noreferrer">
                  {result.pages_url}
                </a>
              ) : (
                "—"
              )}
            </div>
          </div>
        </div>

        <div className="actions">
          <Link to="/" className="btn">Back Home</Link>
          {result.preview_url && (
            <a className="btn secondary" href={result.preview_url} target="_blank" rel="noreferrer">
              Open Preview
            </a>
          )}
          {result.download_url && (
            <a className="btn secondary" href={result.download_url}>
              Download ZIP
            </a>
          )}
          {result.github_url && (
            <a className="btn secondary" href={result.github_url} target="_blank" rel="noreferrer">
              Open Repo
            </a>
          )}
          {result.pages_url && (
            <a className="btn secondary" href={result.pages_url} target="_blank" rel="noreferrer">
              Open Live
            </a>
          )}
        </div>
      </div>

      <div className="card">
        <h3>Generated Code</h3>
        {Object.keys(files).length === 0 ? (
          <div className="hint">No files yet.</div>
        ) : (
          Object.entries(files).map(([name, content]) => (
            <div key={name} style={{ marginBottom: 16 }}>
              <div className="info-label">{name}</div>
              <pre style={{ whiteSpace: "pre-wrap" }}>{content}</pre>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
