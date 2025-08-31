# backend.py
import os
import logging
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from projectCreator import create_project_structure
from model import get_data_from_agent
from githubHandler import deploy_to_github

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECTS_DIR = Path("projects")


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
    """
    Complete pipeline: Generate project from prompt using AI and optionally deploy to GitHub
    
    Args:
        prompt: User's project description
        project_name: Local project directory name
        github_token: GitHub personal access token (required for deployment)
        username: GitHub username (required for deployment)
        repo_name: Repository name (required for deployment)
        auto_deploy: Whether to automatically deploy to GitHub
        img: Path to uploaded image file
        figma_url: Figma design URL (not used in this implementation)
        figma_token: Figma access token (not used in this implementation)
    
    Returns:
        Dict containing project info and deployment status
    """
    
    # Generate project name if not provided
    if not project_name:
        import time
        project_name = f"generated_project_{int(time.time())}"
    
    # Create unique project ID for file organization
    pid = uuid.uuid4().hex[:8]
    project_dir_name = f"site-{pid}"
    
    print(f"🎯 Creating project: {project_dir_name}")
    print(f"📝 User request: {prompt}")
    
    # Step 1: Generate project files using AI
    try:
        agent_result = get_data_from_agent(prompt, img=img)
        
        if not agent_result:
            return {
                "success": False,
                "error": "Failed to generate project files using AI",
                "project_path": None,
                "preview_url": None,
                "download_url": None,
                "github_url": None,
                "pages_url": None,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "files_written": []
            }
    
    except Exception as e:
        logger.error(f"Error in AI generation: {str(e)}")
        return {
            "success": False,
            "error": f"AI generation failed: {str(e)}",
            "project_path": None,
            "preview_url": None,
            "download_url": None,
            "github_url": None,
            "pages_url": None,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "files_written": []
        }
    
    # Step 2: Create local project structure in projects directory
    try:
        PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
        project_path = PROJECTS_DIR / project_dir_name
        
        # Create the project using the AI result
        success = create_project_structure(agent_result, str(project_path))
        
        if not success:
            return {
                "success": False,
                "error": "Failed to create local project structure",
                "project_path": None,
                "preview_url": None,
                "download_url": None,
                "github_url": None,
                "pages_url": None,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "files_written": []
            }
            
    except Exception as e:
        logger.error(f"Error creating project structure: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to create project structure: {str(e)}",
            "project_path": None,
            "preview_url": None,
            "download_url": None,
            "github_url": None,
            "pages_url": None,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "files_written": []
        }
    
    # Generate preview and download URLs for the frontend
    import base64
    b64_path = base64.urlsafe_b64encode(str(project_path).encode()).decode()
    base_url = "https://autogenx.onrender.com"  # Your Render backend URL
    preview_url = f"{base_url}/preview/{b64_path}/"
    download_url = f"{base_url}/download?path={str(project_path)}"
    
    # Get list of created files
    files_created = []
    if agent_result and 'files' in agent_result:
        files_created = list(agent_result['files'].keys())
    
    result = {
        "success": True,
        "project_path": str(project_path),
        "preview_url": preview_url,
        "download_url": download_url,
        "amplified_requirements": agent_result.get('amplified_requirements', {}),
        "files_created": files_created,
        "github_url": None,
        "pages_url": None,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "files_written": files_created
    }
    
    # Step 3: Deploy to GitHub if requested
    if auto_deploy and github_token and username and repo_name:
        print(f"\n🌐 Auto-deploying to GitHub...")
        
        try:
            website_url = deploy_to_github(str(project_path), github_token, username, repo_name)
            
            if website_url:
                result["pages_url"] = website_url
                result["github_url"] = f"https://github.com/{username}/{repo_name}"
                result["deployment_status"] = "success"
                print(f"\n🎉 Project successfully deployed!")
                print(f"🔗 Live website: {website_url}")
            else:
                result["deployment_status"] = "failed"
                print(f"\n⚠️ Local project created but deployment failed")
                
        except Exception as e:
            logger.error(f"Deployment error: {str(e)}")
            result["deployment_status"] = "failed"
            result["deployment_error"] = str(e)
    
    elif auto_deploy:
        result["deployment_status"] = "skipped"
        result["deployment_error"] = "Missing GitHub credentials for deployment"
        print(f"\n⚠️ Deployment skipped: Missing GitHub token, username, or repo name")
    
    return result
