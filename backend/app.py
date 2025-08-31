import os
import io
import zipfile
import base64
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import requests
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, flash, send_from_directory, abort
from flask_cors import CORS

from backend import create_and_deploy_project

def create_app():
    app = Flask(__name__)
    
    # Configure CORS to allow all origins
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    def _extract_figma_key_and_node(figma_url: str):
        try:
            u = urlparse(figma_url)
            parts = [p for p in u.path.split('/') if p]
            key = None
            if len(parts) >= 2 and parts[0] in ("file", "design"):
                key = parts[1]
            q = parse_qs(u.query)
            node = q.get('node-id', [None])[0]
            return key, node
        except Exception:
            return None, None

    def _download_figma_image(figma_url: str, token: str, uploads_dir: Path) -> str | None:
        key, node = _extract_figma_key_and_node(figma_url)
        if not key or not token:
            return None
        headers = {"X-FIGMA-TOKEN": token}
        if not node:
            meta = requests.get(f"https://api.figma.com/v1/files/{key}", headers=headers, timeout=30)
            meta.raise_for_status()
            data = meta.json()
            node = data.get('document', {}).get('children', [{}])[0].get('id')
            if not node:
                return None
        imgs = requests.get(
            f"https://api.figma.com/v1/images/{key}",
            headers=headers,
            params={"ids": node, "format": "png", "scale": 2},
            timeout=30,
        )
        imgs.raise_for_status()
        img_url = imgs.json().get('images', {}).get(node)
        if not img_url:
            return None
        img_resp = requests.get(img_url, timeout=60)
        img_resp.raise_for_status()
        uploads_dir.mkdir(parents=True, exist_ok=True)
        out_path = uploads_dir / f"figma_{key}_{node.replace(':','-')}.png"
        with open(out_path, 'wb') as f:
            f.write(img_resp.content)
        return str(out_path)

    @app.route("/generate", methods=["POST"])
    def generate():
        prompt = request.form.get("prompt", "").strip()
        project_name = request.form.get("project_name", "").strip() or None
        img_path = None
        file = request.files.get("image")
        if file and file.filename:
            uploads_dir = Path("uploads")
            uploads_dir.mkdir(parents=True, exist_ok=True)
            img_path = str(uploads_dir / file.filename)
            file.save(img_path)
        canvas_data = request.form.get("canvas_data", "")
        if canvas_data.startswith("data:image/"):
            try:
                header, b64 = canvas_data.split(",", 1)
                raw = base64.b64decode(b64)
                uploads_dir = Path("uploads")
                uploads_dir.mkdir(parents=True, exist_ok=True)
                img_path = str(uploads_dir / "canvas_wireframe.png")
                with open(img_path, 'wb') as f:
                    f.write(raw)
            except Exception as e:
                flash(f"Canvas image parse failed: {e}", "error")
        figma_url = request.form.get("figma_url", "").strip()
        figma_token = request.form.get("figma_token") or os.getenv("FIGMA_TOKEN")
        if figma_url:
            try:
                img_from_figma = _download_figma_image(figma_url, figma_token, Path("uploads"))
                if img_from_figma:
                    img_path = img_from_figma
                else:
                    flash("Unable to render Figma file. Check URL and token.", "error")
            except Exception as e:
                flash(f"Figma fetch failed: {e}", "error")
        auto_deploy = request.form.get("auto_deploy") == "on"
        username = request.form.get("github_username") or None
        repo_name = request.form.get("repo_name") or None
        token = request.form.get("github_token") or os.getenv("GITHUB_TOKEN")
        if not prompt:
            flash("Prompt is required", "error")
            return redirect(url_for("index"))
        result = create_and_deploy_project(
            prompt=prompt,
            project_name=project_name,
            github_token=token if auto_deploy else None,
            username=username if auto_deploy else None,
            repo_name=repo_name if auto_deploy else None,
            auto_deploy=auto_deploy,
            img=img_path,
        )
        if not result.get("success"):
            flash(result.get("error", "Generation failed"), "error")
            return redirect(url_for("index"))
        return render_template("result.html", result=result)

    @app.route("/api/generate", methods=["POST"])
    def generate_api():
        prompt = request.form.get("prompt", "").strip()
        project_name = request.form.get("project_name", "").strip() or None
        img_path = None
        file = request.files.get("image")
        if file and file.filename:
            uploads_dir = Path("uploads")
            uploads_dir.mkdir(parents=True, exist_ok=True)
            img_path = str(uploads_dir / file.filename)
            file.save(img_path)
        canvas_data = request.form.get("canvas_data", "")
        if canvas_data.startswith("data:image/"):
            try:
                header, b64 = canvas_data.split(",", 1)
                raw = base64.b64decode(b64)
                uploads_dir = Path("uploads")
                uploads_dir.mkdir(parents=True, exist_ok=True)
                img_path = str(uploads_dir / "canvas_wireframe.png")
                with open(img_path, 'wb') as f:
                    f.write(raw)
            except Exception as e:
                return jsonify({"success": False, "error": f"Canvas image parse failed: {e}"}), 400
        figma_url = request.form.get("figma_url", "").strip()
        figma_token = request.form.get("figma_token") or os.getenv("FIGMA_TOKEN")
        if figma_url:
            try:
                img_from_figma = _download_figma_image(figma_url, figma_token, Path("uploads"))
                if img_from_figma:
                    img_path = img_from_figma
                else:
                    return jsonify({"success": False, "error": "Unable to render Figma file. Check URL and token."}), 400
            except Exception as e:
                return jsonify({"success": False, "error": f"Figma fetch failed: {e}"}), 400
        auto_deploy = request.form.get("auto_deploy") == "on"
        username = request.form.get("github_username") or None
        repo_name = request.form.get("repo_name") or None
        token = request.form.get("github_token") or os.getenv("GITHUB_TOKEN")
        if not prompt:
            return jsonify({"success": False, "error": "Prompt is required"}), 400
        
        # Check if Google API key is available
        if not os.getenv("GOOGLE_API_KEY"):
            return jsonify({
                "success": False, 
                "error": "AI service is not configured. Please contact the administrator."
            }), 503
            
        try:
            result = create_and_deploy_project(
                prompt=prompt,
                project_name=project_name,
                github_token=token if auto_deploy else None,
                username=username if auto_deploy else None,
                repo_name=repo_name if auto_deploy else None,
                auto_deploy=auto_deploy,
                img=img_path,
            )
            return jsonify(result)
        except Exception as e:
            print(f"Error in project generation: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"Project generation failed: {str(e)}"
            }), 500

    @app.route("/download", methods=["GET"])
    def download():
        project_path = request.args.get("path")
        if not project_path or not os.path.isdir(project_path):
            flash("Invalid project path", "error")
            return redirect(url_for("index"))
        mem = io.BytesIO()
        with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(project_path):
                for f in files:
                    full = os.path.join(root, f)
                    arcname = os.path.relpath(full, project_path)
                    zf.write(full, arcname)
        mem.seek(0)
        proj = Path(project_path).name
        return send_file(mem, as_attachment=True, download_name=f"{proj}.zip")

    def _safe_join(base: str, rel: str) -> str:
        base_real = os.path.realpath(base)
        target = os.path.realpath(os.path.join(base_real, rel))
        if target == base_real or target.startswith(base_real + os.sep):
            return target
        raise PermissionError("Path traversal detected")

    @app.route("/preview/<b64base>/", defaults={"relpath": ""})
    @app.route("/preview/<b64base>/<path:relpath>")
    def preview_file(b64base: str, relpath: str):
        try:
            base = base64.urlsafe_b64decode(b64base.encode()).decode()
        except Exception:
            abort(400)
        if not os.path.isdir(base):
            abort(404)
        rel = relpath or "index.html"
        try:
            full = _safe_join(base, rel)
        except PermissionError:
            abort(403)
        if os.path.isdir(full):
            rel = os.path.join(rel, "index.html") if rel else "index.html"
        return send_from_directory(base, rel, conditional=True)

    @app.route("/api/files", methods=["GET"])
    def api_files():
        path = request.args.get('path', '')
        if not path:
            return jsonify({"error": "No path provided"}), 400
        
        # Convert projects/site-xxx to actual file path
        full_path = Path(path)
        if not full_path.exists():
            return jsonify({"error": f"Project path '{path}' not found"}), 404
        
        files = {}
        try:
            for file_path in full_path.iterdir():
                if file_path.is_file():
                    files[file_path.name] = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return jsonify({"error": f"Error reading files: {str(e)}"}), 500
        
        return jsonify(files)

    return app

app = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=debug, use_reloader=False)
