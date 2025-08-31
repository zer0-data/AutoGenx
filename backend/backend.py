
import os, uuid, textwrap
from pathlib import Path
from datetime import datetime

try:
    from githubHandler import create_or_update_repo, enable_pages_and_push
except Exception:
    create_or_update_repo = None
    enable_pages_and_push = None

PROJECTS_DIR = Path("projects")

def _scaffold_from_prompt(prompt: str) -> dict[str, str]:
    title = (prompt or "Generated Site").strip().capitalize()
    wants_form = "form" in prompt.lower()
    fields = []
    if "name" in prompt.lower(): fields.append(("name", "text", "Your name"))
    if "email" in prompt.lower(): fields.append(("email", "email", "Email address"))
    if "phone" in prompt.lower(): fields.append(("phone", "tel", "Phone"))
    if "age" in prompt.lower(): fields.append(("age", "number", "Age"))
    if "ticket" in prompt.lower(): fields.append(("tickets", "number", "No. of tickets"))
    if not fields and wants_form:
        fields = [("name", "text", "Your name")]
    red_theme = "red" in prompt.lower()
    css = f"""
    :root {{
      --primary: {"#c81d25" if red_theme else "#119da4"};
      --bg: #ffffff;
      --text: #111;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, Inter, Arial, sans-serif;
      </head>
    return {
      "success": False,
      "error": "Project folder could not be created.",
      "project_path": project_path,
      "github_url": None,
      "pages_url": None,
      "generated_at": datetime.utcnow().isoformat() + "Z",
      "files_written": [],
    }

  if auto_deploy and github_token and username and repo_name:
    try:
      if create_or_update_repo and enable_pages_and_push:
        # These helpers are expected to handle: repo create/clean, push files, enable Pages
        github_url = create_or_update_repo(
          username=username,
          repo_name=repo_name,
          token=github_token,
          local_path=project_path,
        )
        pages_url = enable_pages_and_push(
          username=username,
          repo_name=repo_name,
          token=github_token,
          local_path=project_path,
        )
      else:
        # Graceful no-op if GH helper not available
        pass
    except Exception as e:
      # Do not fail the generation if deploy fails
      print(f"[deploy] error: {e}")

  return {
    "success": True,
    "project_path": project_path,
    "github_url": github_url,
    "pages_url": pages_url,
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "files_written": ["index.html", "styles.css", "script.js"],
  }
