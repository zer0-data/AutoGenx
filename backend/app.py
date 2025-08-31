# app.py
import os, io, zipfile, base64
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import requests
from flask import Flask, request, jsonify, send_file, send_from_directory, abort
import inspect

from backend import create_and_deploy_project


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

    # ----------------------
    # Helpers
    # ----------------------
    def _safe_join(base: str, rel: str) -> str:
        base_real = os.path.realpath(base)
        target = os.path.realpath(os.path.join(base_real, rel))
        if target == base_real or target.startswith(base_real + os.sep):
            return target
        raise PermissionError("Path traversal detected")

    def _extract_figma_key_and_node(figma_url: str):
        try:
            u = urlparse(figma_url)
            parts = [p for p in u.path.split("/") if p]
            key = None
            if len(parts) >= 2 and parts[0] in ("file", "design"):
                key = parts[1]
            q = parse_qs(u.query)
            node = q.get("node-id", [None])[0]
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
            node = data.get("document", {}).get("children", [{}])[0].get("id")
            if not node:
                return None

        imgs = requests.get(
            f"https://api.figma.com/v1/images/{key}",
            headers=headers,
            params={"ids": node, "format": "png", "scale": 2},
            timeout=30,
        )
        imgs.raise_for_status()
        img_url = imgs.json().get("images", {}).get(node)
        if not img_url:
            return None

        img_resp = requests.get(img_url, timeout=60)
        img_resp.raise_for_status()
        uploads_dir.mkdir(parents=True, exist_ok=True)
        out_path = uploads_dir / f"figma_{key}_{node.replace(':','-')}.png"
        out_path.write_bytes(img_resp.content)
        return str(out_path)

    def _save_canvas_png(data_url: str, dest_dir: Path) -> str | None:
        if not data_url or not data_url.startswith("data:image/"):
            return None
        try:
            _, b64 = data_url.split(",", 1)
            raw = base64.b64decode(b64)
            dest_dir.mkdir(parents=True, exist_ok=True)
            out = dest_dir / "canvas_wireframe.png"
            out.write_bytes(raw)
            return str(out)
        except Exception:
            return None

    def _save_uploaded_file(file_storage, dest_dir: Path) -> str | None:
        if not file_storage or not getattr(file_storage, "filename", ""):
            return None
        dest_dir.mkdir(parents=True, exist_ok=True)
        out = dest_dir / file_storage.filename
        file_storage.save(out)
        return str(out)

    def _call_backend_with_supported_kwargs(**kwargs):
        """
        Call create_and_deploy_project but only pass kwargs it actually supports.
        This avoids 'unexpected keyword argument' errors across different versions.
        """
        sig = inspect.signature(create_and_deploy_project)
        allowed = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return create_and_deploy_project(**allowed)

    # ----------------------
    # API
    # ----------------------
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/api/generate")
    def generate():
        uploads = Path("uploads")

        # Accept JSON or multipart form
        data_json = request.get_json(silent=True)
        if data_json:
            description = (data_json.get("description") or data_json.get("prompt") or "").strip()
            project_name = (data_json.get("project_name") or "").strip() or None
            auto_deploy = bool(data_json.get("auto_deploy", False))
            username = (data_json.get("github_username") or "").strip() or None
            repo_name = (data_json.get("repo_name") or "").strip() or None
            token = (data_json.get("github_token") or os.getenv("GITHUB_TOKEN") or "").strip() or None
            figma_url = (data_json.get("figma_url") or "").strip()
            figma_token = (data_json.get("figma_token") or os.getenv("FIGMA_TOKEN") or "").strip()
            img_path = None
        else:
            form = request.form
            files = request.files
            description = (form.get("prompt") or form.get("description") or "").strip()
            project_name = (form.get("project_name") or "").strip() or None
            auto_deploy = (form.get("auto_deploy") or "").lower() in ("on", "true", "1", "yes")
            username = (form.get("github_username") or "").strip() or None
            repo_name = (form.get("repo_name") or "").strip() or None
            token = (form.get("github_token") or os.getenv("GITHUB_TOKEN") or "").strip() or None
            figma_url = (form.get("figma_url") or "").strip()
            figma_token = (form.get("figma_token") or os.getenv("FIGMA_TOKEN") or "").strip()
            img_path = _save_uploaded_file(files.get("image"), uploads)
            canvas_data_url = form.get("canvas_data")
            if canvas_data_url and not img_path:
                img_path = _save_canvas_png(canvas_data_url, uploads)

        if not description:
            return jsonify({"success": False, "error": "Description is required"}), 400

        # If Figma info is present, render a PNG and use as `img_path` (local hint)
        if figma_url and figma_token and not img_path:
            try:
                img_found = _download_figma_image(figma_url, figma_token, uploads)
                if img_found:
                    img_path = img_found
            except Exception:
                pass  # non-fatal

        # Call backend with only supported kwargs
        try:
            result = _call_backend_with_supported_kwargs(
                prompt=description,
                project_name=project_name,
                github_token=(token if auto_deploy else None),
                username=(username if auto_deploy else None),
                repo_name=(repo_name if auto_deploy else None),
                auto_deploy=auto_deploy,
                img=img_path,
                # figma_url / figma_token intentionally NOT passed unless backend supports them
            )
        except Exception as e:
            app.logger.exception("create_and_deploy_project failed: %s", e)
            return jsonify({"success": False, "error": str(e)}), 500

        if not result or not result.get("success"):
            return jsonify({"success": False, "error": "Generation failed"}), 500

        project_path = result.get("project_path")
        if not project_path or not os.path.isdir(project_path):
            return jsonify({"success": False, "error": "Project path missing"}), 500

        b64base = base64.urlsafe_b64encode(project_path.encode()).decode()
        preview_url = f"/api/preview/{b64base}/index.html"
        download_url = f"/api/download?path={project_path}"

        return jsonify({
            "success": True,
            "project_path": project_path,
            "github_url": result.get("github_url"),
            "pages_url": result.get("pages_url"),
            "preview_url": preview_url,
            "download_url": download_url,
        })

    @app.get("/api/download")
    def download():
        project_path = request.args.get("path")
        if not project_path or not os.path.isdir(project_path):
            return jsonify({"error": "Invalid project path"}), 400

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

    @app.get("/api/files")
    def list_files():
        """
        Returns { files: { "index.html": "<content>", ... } } so the UI can show code.
        """
        project_path = request.args.get("path")
        if not project_path or not os.path.isdir(project_path):
            return jsonify({"error": "Invalid project path"}), 400

        out = {}
        for p in Path(project_path).glob("*"):
            if p.is_file() and p.suffix in (".html", ".css", ".js", ".json"):
                try:
                    out[p.name] = p.read_text(encoding="utf-8")
                except Exception:
                    out[p.name] = "// (binary or unreadable)"
        return jsonify({"files": out})

    @app.get("/api/preview/<b64base>/", defaults={"relpath": ""})
    @app.get("/api/preview/<b64base>/<path:relpath>")
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


app = create_app()

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5500)), debug=debug, use_reloader=False)
