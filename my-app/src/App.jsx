import React, { useEffect } from "react";

function App() {
  useEffect(() => {
    // Canvas drawing logic
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
    const hidden = document.getElementById("canvas_data");

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
      hidden.value = "";
    });
  }, []);

  return (
    <div className="wrap">
      <header className="glow-effect">
        <h1>Autogen</h1>
        <p>
          Turn a prompt or screenshot into a deployable website. Optionally
          auto-deploy to GitHub Pages.
        </p>
      </header>

      <form>
        <div className="form-grid">
          <div className="card prompt-section">
            <label htmlFor="prompt">Project Description</label>
            <textarea
              id="prompt"
              name="prompt"
              placeholder="Describe the website..."
            ></textarea>
            <div className="hint">
              Be as specific as possible - mention colors, layout, features, and
              functionality you want.
            </div>
          </div>

          <div className="card">
            <label htmlFor="project_name">Project Name</label>
            <input
              type="text"
              id="project_name"
              placeholder="Leave empty for auto-generation"
            />
          </div>

          <div className="card">
            <label htmlFor="image">Reference Image</label>
            <input type="file" id="image" accept="image/*" />
          </div>

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
            <input type="hidden" id="canvas_data" />
          </div>

          <div className="card deploy-section">
            <label className="checkbox-label">
              <input type="checkbox" /> Auto-deploy to GitHub Pages
            </label>
            <div className="deploy-inputs">
              <input type="text" placeholder="GitHub username" />
              <input type="text" placeholder="Repository name" />
              <input type="password" placeholder="GitHub token" />
            </div>
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
