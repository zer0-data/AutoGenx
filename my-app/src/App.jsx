import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./App.css"; // keep your CSS

function App() {
  const [prompt, setPrompt] = useState("");
  const [projectName, setProjectName] = useState("");
  const [username, setUsername] = useState("");
  const [repoName, setRepoName] = useState("");
  const [token, setToken] = useState("");
  const [autoDeploy, setAutoDeploy] = useState(false);
  const [figmaUrl, setFigmaUrl] = useState("");
  const [figmaToken, setFigmaToken] = useState("");
  const [image, setImage] = useState(null);
  const [canvasData, setCanvasData] = useState("");

  const navigate = useNavigate();

  // ✅ Canvas drawing logic
  useEffect(() => {
    const canvas = document.getElementById("wireCanvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let drawing = false;
    let lastX = 0,
      lastY = 0;
    let isDirty = false;

    const colorEl = document.getElementById("penColor");
    const sizeEl = document.getElementById("penSize");
    const clearBtn = document.getElementById("clearCanvas");

    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    function getPos(e) {
      const rect = canvas.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      return {
        x: (clientX - rect.left) * (canvas.width / rect.width),
        y: (clientY - rect.top) * (canvas.height / rect.height),
      };
    }

    function start(e) {
      drawing = true;
      isDirty = true;
      const p = getPos(e);
      lastX = p.x;
      lastY = p.y;
    }
    function move(e) {
      if (!drawing) return;
      const p = getPos(e);
      ctx.strokeStyle = colorEl.value;
      ctx.lineWidth = Number(sizeEl.value);
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.beginPath();
      ctx.moveTo(lastX, lastY);
      ctx.lineTo(p.x, p.y);
      ctx.stroke();
      lastX = p.x;
      lastY = p.y;
      e.preventDefault();
    }
    function end() {
      drawing = false;
    }

    canvas.addEventListener("mousedown", start);
    canvas.addEventListener("mousemove", move);
    window.addEventListener("mouseup", end);
    canvas.addEventListener("touchstart", start, { passive: false });
    canvas.addEventListener("touchmove", move, { passive: false });
    canvas.addEventListener("touchend", end);

    clearBtn.addEventListener("click", () => {
      ctx.fillStyle = "#ffffff";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      isDirty = false;
      setCanvasData("");
    });

    // capture image on submit
    const form = document.getElementById("genForm");
    if (form) {
      form.addEventListener("submit", () => {
        if (isDirty) {
          setCanvasData(canvas.toDataURL("image/png"));
        }
      });
    }

    return () => {
      canvas.removeEventListener("mousedown", start);
      canvas.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", end);
      canvas.removeEventListener("touchstart", start);
      canvas.removeEventListener("touchmove", move);
      canvas.removeEventListener("touchend", end);
    };
  }, []);

  // ✅ Handle form submit
  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("project_name", projectName);
    formData.append("auto_deploy", autoDeploy ? "on" : "");
    formData.append("github_username", username);
    formData.append("repo_name", repoName);
    formData.append("github_token", token);
    formData.append("figma_url", figmaUrl);
    formData.append("figma_token", figmaToken);
    if (image) formData.append("image", image);
    if (canvasData) formData.append("canvas_data", canvasData);

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.success) {
        navigate("/result", { state: data });
      } else {
        alert(data.error || "Generation failed");
      }
    } catch (err) {
      console.error("Request failed:", err);
      alert("Server error");
    }
  };

  return (
    <div className="wrap">
      <header className="glow-effect">
        <h1>Autogen</h1>
        <p>
          Turn a prompt or screenshot into a deployable website. Optionally
          auto-deploy to GitHub Pages.
        </p>
      </header>

      <form id="genForm" onSubmit={handleSubmit}>
        <div className="form-grid">
          {/* Prompt */}
          <div className="card prompt-section">
            <label htmlFor="prompt">Project Description</label>
            <textarea
              id="prompt"
              name="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the website you want to create..."
            />
            <div className="hint">
              Be as specific as possible – mention colors, layout, features, and
              functionality.
            </div>
          </div>

          {/* Project Name */}
          <div className="card">
            <label htmlFor="project_name">Project Name</label>
            <input
              type="text"
              id="project_name"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="Leave empty for auto-generation"
            />
          </div>

          {/* Image Upload */}
          <div className="card">
            <label htmlFor="image">Reference Image</label>
            <input
              type="file"
              id="image"
              accept="image/*"
              onChange={(e) => setImage(e.target.files[0])}
            />
            <div className="hint">
              Upload a design mockup, screenshot, or inspiration image.
            </div>
          </div>

          {/* Canvas */}
          <div className="card canvas-section">
            <label>Quick Wireframe Sketch</label>
            <div className="canvas-controls">
              <div className="tool">
                <label>Color</label>
                <input type="color" id="penColor" defaultValue="#000000" />
              </div>
              <div className="tool">
                <label>Brush Size</label>
                <input type="range" id="penSize" min="1" max="20" defaultValue="3" />
              </div>
              <button type="button" id="clearCanvas">
                Clear Canvas
              </button>
            </div>
            <canvas id="wireCanvas" width="900" height="560"></canvas>
            <input type="hidden" id="canvas_data" value={canvasData} />
            <div className="hint">
              Draw a rough layout or wireframe to guide the design.
            </div>
          </div>

          {/* Figma */}
          <div className="card">
            <label htmlFor="figma_url">Figma Design File</label>
            <input
              type="text"
              id="figma_url"
              value={figmaUrl}
              onChange={(e) => setFigmaUrl(e.target.value)}
              placeholder="https://www.figma.com/file/[key]/..."
            />
            <input
              type="password"
              value={figmaToken}
              onChange={(e) => setFigmaToken(e.target.value)}
              placeholder="Figma token"
              style={{ marginTop: "12px" }}
            />
          </div>

          {/* Deploy */}
          <div className="card deploy-section">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={autoDeploy}
                onChange={(e) => setAutoDeploy(e.target.checked)}
              />
              Auto-deploy to GitHub Pages
            </label>
            {autoDeploy && (
              <div className="deploy-inputs">
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="GitHub username"
                />
                <input
                  type="text"
                  value={repoName}
                  onChange={(e) => setRepoName(e.target.value)}
                  placeholder="Repository name"
                />
                <input
                  type="password"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="GitHub token"
                />
              </div>
            )}
          </div>
        </div>

        <div className="actions">
          <button type="submit">Generate & Deploy</button>
        </div>
      </form>
    </div>
  );
}

export default App;
