## Autogen (Flask Web App)

Autogen provides a simple web UI to generate and optionally deploy a website from a prompt, a sketch, an uploaded image, or a Figma wireframe.

### Setup

1) Create and activate a virtual environment (optional but recommended)
2) Install dependencies
3) Set your API key environment variables

PowerShell (Windows):

```
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GOOGLE_API_KEY = "<your-gemini-api-key>"
# optional for auto-deploy from UI
$env:GITHUB_TOKEN = "<your-github-personal-access-token>"
# optional secret for Flask sessions
$env:FLASK_SECRET_KEY = "change-me"
# optional for Figma rendering
$env:FIGMA_TOKEN = "<your-figma-personal-access-token>"
```

### Run

```
python app.py
```

Open http://localhost:5000 in your browser.

### Notes

- For auto-deploy to GitHub Pages from the UI, provide Username, Repo, and Token in the form, or set GITHUB_TOKEN in env and leave the field blank.
- Model API key is read from environment variable GOOGLE_API_KEY (no hardcoded secrets).
- Generated project can be downloaded as a .zip.
- A Preview panel shows the generated project directly in the app.

### Figma wireframe support

- Provide a Figma file URL in the form and a Figma personal access token.
- We render the first page of the file to a PNG and use it as the design reference.
- Optionally set FIGMA_TOKEN as an environment variable to avoid typing it each time.

### Canvas sketch support

- Draw a quick wireframe in the built-in canvas; it’s uploaded as a PNG and used as the reference image.
- You can also upload a screenshot/mockup; canvas, upload, and Figma are all optional.

### In-app Preview

- After generation, the Results page includes a Preview section with an embedded iframe.
- “Open Local” previews the generated project files served from your local output folder.
- If you deployed to GitHub Pages, “Open Live” previews the live site.



## 🛠️ Prerequisites

Before you begin, ensure you have the following:

- Python 3.8 or higher
- Git installed on your system
- GitHub account
- Google Cloud account (for Gemini API)



## 📦 Requirements

### Python Dependencies (`requirements.txt`)

```
annotated-types==0.7.0
anyio==4.9.0
cachetools==5.5.2
certifi==2025.4.26
charset-normalizer==3.4.2
google-auth==2.40.2
google-genai==1.16.1
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.10
pyasn1==0.6.1
pyasn1_modules==0.4.2
pydantic==2.11.4
pydantic_core==2.33.2
requests==2.32.3
rsa==4.9.1
sniffio==1.3.1
typing-inspection==0.4.1
typing_extensions==4.13.2
urllib3==2.4.0
websockets==15.0.1
Flask==3.0.3
```

### System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM
- **Storage**: 1GB free space
- **Internet**: Required for AI API calls and GitHub operations

## 🎯 Examples

### Example 1: Text-Based Generation
```
Do you wanna give image input(y/n)?:- n
🎯 Describe the project you want to create: Create a minimal portfolio website for a UX designer
📁 Project name (press Enter for auto-generated): ux-portfolio
🚀 Deploy to GitHub? (y/n): y
📦 Repository name (default: ux-portfolio): 
```

### Example 2: Image-Based Generation
```
Do you wanna give image input(y/n)?:- y
Enter the image path: ./designs/mockup.png
🎯 Describe the project you want to create: Replicate this restaurant website design
📁 Project name (press Enter for auto-generated): restaurant-site
🚀 Deploy to GitHub? (y/n): y
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request



## 🙏 Acknowledgments

- Google Gemini AI for code generation
- GitHub for hosting and deployment
- Unsplash for placeholder images
- The open-source community for inspiration




