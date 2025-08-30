import React from "react";

function Result() {
  return (
    <div className="wrap">
      <h1>Project Generated</h1>
      <div className="card">
        <h3>Deployment Info</h3>
        <div className="info-grid">
          <div className="info-item">
            <div className="info-label">Repo</div>
            <div className="info-value">username/repo</div>
          </div>
          <div className="info-item">
            <div className="info-label">URL</div>
            <div className="info-value">
              <a href="https://username.github.io/repo">
                https://username.github.io/repo
              </a>
            </div>
          </div>
        </div>
        <div className="actions">
          <a href="/" className="btn">
            Back Home
          </a>
          <a href="https://username.github.io/repo" className="btn secondary">
            Open Live
          </a>
        </div>
      </div>
    </div>
  );
}

export default Result;
