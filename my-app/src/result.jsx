// result.jsx
import React, { useEffect, useState, useMemo } from "react";
import { useLocation, Link, useNavigate } from "react-router-dom";
import "./Result.css";

export default function Result() {
  const { state } = useLocation(); // data from navigate("/result", { state: data })
  const navigate = useNavigate();
  const result = state || {};
  const [files, setFiles] = useState({});
  const [toast, setToast] = useState("");

  const hasAnyUrl = useMemo(
    () =>
      Boolean(
        result.preview_url ||
          result.download_url ||
          result.github_url ||
          result.pages_url
      ),
    [result]
  );

  useEffect(() => {
    const fetchFiles = async () => {
      if (!result.project_path) return;
      const q = new URLSearchParams({ path: result.project_path });
      try {
        const res = await fetch(`/api/files?${q.toString()}`);
        const data = await res.json();
        if (data && data.files) setFiles(data.files);
      } catch (e) {
        // no-op
      }
    };
    fetchFiles();
  }, [result.project_path]);

  const copy = async (text, label = "Copied!") => {
    try {
      await navigator.clipboard.writeText(text);
      setToast(label);
      setTimeout(() => setToast(""), 1500);
    } catch {
      setToast("Copy failed");
      setTimeout(() => setToast(""), 1500);
    }
  };

  const open = (url) => {
    if (!url) return;
    window.open(url, "_blank", "noopener,noreferrer");
  };

  const goHome = () => navigate("/");

  return (
    <div className="wrap">
      <h1>Project Generated</h1>

      {/* Quick action toolbar */}
      <div className="toolbar card">
        <div className="toolbar-left">
          <span className="pill">Project</span>
          <code className="mono">{result.project_path || "—"}</code>
        </div>

        <div className="toolbar-right">
          <button className="btn secondary" onClick={goHome}>
            Back Home
          </button>

          {result.preview_url && (
            <>
              <button
                className="btn"
                onClick={() => open(result.preview_url)}
                id="openLocal"
                title="Local preview"
              >
                Open Preview
              </button>
              <button
                className="btn ghost"
                onClick={() => copy(result.preview_url, "Preview URL copied")}
                aria-label="Copy preview URL"
              >
                Copy Preview URL
              </button>
            </>
          )}

          {result.download_url && (
            <a className="btn secondary" href={result.download_url}>
              Download ZIP
            </a>
          )}

          {result.github_url && (
            <>
              <button
                className="btn secondary"
                onClick={() => open(result.github_url)}
                title="Open repository"
              >
                Open Repo
              </button>
              <button
                className="btn ghost"
                onClick={() => copy(result.github_url, "Repo URL copied")}
                aria-label="Copy repo URL"
              >
                Copy Repo URL
              </button>
            </>
          )}

          {result.pages_url && (
            <>
              <button
                className="btn"
                onClick={() => open(result.pages_url)}
                id="openLive"
                title="Open GitHub Pages site"
              >
                Open Live
              </button>
              <button
                className="btn ghost"
                onClick={() => copy(result.pages_url, "Pages URL copied")}
                aria-label="Copy Pages URL"
              >
                Copy Live URL
              </button>
            </>
          )}
        </div>
      </div>

      {/* Summary card */}
      <div className="card">
        <h3>Deployment Info</h3>
        <div className="info-grid">
          <div className="info-item">
            <div className="info-label">Preview</div>
            <div className="info-value">
              {result.preview_url ? (
                <>
                  <a href={result.preview_url} target="_blank" rel="noreferrer">
                    {result.preview_url}
                  </a>
                  <button
                    className="linklike kbd"
                    onClick={() => copy(result.preview_url)}
                  >
                    Copy
                  </button>
                </>
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
                <>
                  <a href={result.github_url} target="_blank" rel="noreferrer">
                    {result.github_url}
                  </a>
                  <button
                    className="linklike kbd"
                    onClick={() => copy(result.github_url)}
                  >
                    Copy
                  </button>
                </>
              ) : (
                "—"
              )}
            </div>
          </div>

          <div className="info-item">
            <div className="info-label">Pages URL</div>
            <div className="info-value">
              {result.pages_url ? (
                <>
                  <a href={result.pages_url} target="_blank" rel="noreferrer">
                    {result.pages_url}
                  </a>
                  <button
                    className="linklike kbd"
                    onClick={() => copy(result.pages_url)}
                  >
                    Copy
                  </button>
                </>
              ) : (
                "—"
              )}
            </div>
          </div>
        </div>

        {!hasAnyUrl && (
          <div className="hint">
            No deployment links yet. You can still download the ZIP above and
            deploy manually.
          </div>
        )}

        <div className="actions">
          <Link to="/" className="btn">
            Make Another
          </Link>
          {result.preview_url && (
            <a
              className="btn secondary"
              href={result.preview_url}
              target="_blank"
              rel="noreferrer"
            >
              Open Preview
            </a>
          )}
          {result.download_url && (
            <a className="btn secondary" href={result.download_url}>
              Download ZIP
            </a>
          )}
          {result.github_url && (
            <a
              className="btn secondary"
              href={result.github_url}
              target="_blank"
              rel="noreferrer"
            >
              Open Repo
            </a>
          )}
          {result.pages_url && (
            <a
              className="btn secondary"
              href={result.pages_url}
              target="_blank"
              rel="noreferrer"
            >
              Open Live
            </a>
          )}
        </div>
      </div>

      <div className="card preview-section">
        <h3>Generated Code</h3>
        {Object.keys(files).length === 0 ? (
          <div className="hint">No files yet.</div>
        ) : (
          Object.entries(files).map(([name, content]) => (
            <div key={name} className="code-block">
              <div className="code-block__header">
                <span className="badge">{name}</span>
                <div className="code-block__actions">
                  <button
                    className="btn tiny ghost"
                    onClick={() => copy(content, `${name} copied`)}
                  >
                    Copy File
                  </button>
                  <button
                    className="btn tiny ghost"
                    onClick={() =>
                      copy(
                        `<a href="${result.preview_url?.replace(
                          /index\.html$/,
                          name
                        )}" target="_blank" rel="noreferrer">${name}</a>`
                      )
                    }
                  >
                    Copy Link HTML
                  </button>
                </div>
              </div>
              <pre className="code-pre" aria-label={`Source of ${name}`}>
                {content}
              </pre>
            </div>
          ))
        )}
      </div>

      {!!toast && <div className="success-indicator">{toast}</div>}
    </div>
  );
}
