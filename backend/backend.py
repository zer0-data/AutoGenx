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
  if "name" in prompt.lower():
    fields.append(("name", "text", "Your name"))
  if "email" in prompt.lower():
    fields.append(("email", "email", "Email address"))
  if "phone" in prompt.lower():
    fields.append(("phone", "tel", "Phone"))
  if "age" in prompt.lower():
    fields.append(("age", "number", "Age"))
  if "ticket" in prompt.lower():
    fields.append(("tickets", "number", "No. of tickets"))
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
    color: var(--text); background: var(--bg);
  }}
  .wrap {{ max-width: 960px; margin: 0 auto; padding: 32px 20px; }}
  h1 {{ margin: 0 0 20px; }}
  .card {{
    background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 24px;
    box-shadow: 0 8px 24px rgba(0,0,0,.06);
  }}
  label {{ font-weight: 600; display:block; margin: 16px 0 8px; }}
  input, textarea, select {{ width: 100%; padding: 12px 14px; border: 1px solid #d1d5db; border-radius: 10px; }}
  button {{
    margin-top: 16px; background: var(--primary); color: #fff; border: 0; border-radius: 10px; padding: 12px 18px; cursor: pointer;
  }}
  button:hover {{ opacity: .9; }}
  .hint {{ color: #6b7280; font-size: 14px; margin-top: 8px; }}
  .banner {{ background: rgba(200,29,37,.07); border: 1px dashed rgba(200,29,37,.4); padding: 12px 14px; border-radius: 10px; margin: 16px 0; }}
  """
    if wants_form:
        fields_html = "\n".join(
            f"""<label htmlFor=\"{name}\">{placeholder}</label>\n<input id=\"{name}\" name=\"{name}\" type=\"{typ}\" placeholder=\"{placeholder}\" required />"""
            for (name, typ, placeholder) in fields
        )
        form_html = f"""
        <div class=\"card\">
          <h2>Register for the event</h2>
          <form id=\"eventForm\">
            {fields_html}
            <label htmlFor=\"message\">Message</label>
            <textarea id=\"message\" name=\"message\" placeholder=\"Anything else?\"></textarea>
            <button type=\"submit\">Submit</button>
            <div id=\"status\" class=\"hint\"></div>
          </form>
        </div>
        """
        js = """
        document.getElementById('eventForm')?.addEventListener('submit', (e) => {
          e.preventDefault();
          const data = Object.fromEntries(new FormData(e.currentTarget).entries());
          const status = document.getElementById('status');
          status.textContent = 'Submitting...';
          setTimeout(() => {
            status.textContent = '✅ Submitted! ' + JSON.stringify(data);
            e.currentTarget.reset();
          }, 600);
        });
        """
    else:
        form_html = """
        <div class=\"card\">
          <h2>Welcome</h2>
          <p>This site was generated automatically from your prompt.</p>
        </div>
        """
        js = "// no dynamic logic for this page\n"
    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{title}</title>
  <link rel=\"stylesheet\" href=\"styles.css\" />
</head>
<body>
  <div class=\"wrap\">
    <h1>{title}</h1>
    <div class=\"banner\"><strong>Prompt:</strong> {prompt}</div>
    {form_html}
  </div>
  <script src=\"script.js\"></script>
</body>
</html>
"""
    return {
        "index.html": textwrap.dedent(html).strip(),
        "styles.css": textwrap.dedent(css).strip(),
        "script.js": textwrap.dedent(js).strip(),
    }

def _write_project(files: dict[str, str]) -> str:
    try:
        PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        pid = uuid.uuid4().hex[:8]
        project_dir = PROJECTS_DIR / f"site-{pid}"
        project_dir.mkdir(parents=True, exist_ok=True)
        for name, content in files.items():
            (project_dir / name).write_text(content, encoding="utf-8")
        print(f"[backend] Project created: {project_dir}")
        return str(project_dir)
    except Exception as e:
        print(f"[backend] Error creating project: {e}")
        return ""

def create_and_deploy_project(
    prompt: str,
    project_name: str | None = None,
    github_token: str | None = None,
    username: str | None = None,
    repo_name: str | None = None,
    auto_deploy: bool = False,
    img: str | None = None,
    figma_url: str | None = None,
    figma_token: str | None = None,
) -> dict:
    files = _scaffold_from_prompt(prompt or "Generated Site")
    project_path = _write_project(files)
    github_url = None
    pages_url = None
    if not project_path or not os.path.isdir(project_path):
        print(f"[backend] Project creation failed: {project_path}")
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
        except Exception as e:
            print(f"[deploy] error: {e}")
    return {
        "success": True,
        "project_path": project_path,
        "github_url": github_url,
        "pages_url": pages_url,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "files_written": ["index.html", "styles.css", "script.js"],
    }

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
      }}
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
