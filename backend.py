import os
import logging
from pathlib import Path
from typing import Dict, Any

from projectCreator import create_project_structure
from model import get_data_from_agent
from githubHandler import deploy_to_github


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





# GitHub Hosting Integration
import base64
import requests


def create_and_deploy_project(prompt: str, project_name: str = None, 
                            github_token: str = None, username: str = None, 
                            repo_name: str = None, auto_deploy: bool = False,img:str = None) -> Dict[str, Any]:
    """
    Complete pipeline: Generate project from prompt and optionally deploy to GitHub
    
    Args:
        prompt: User's project description
        project_name: Local project directory name
        github_token: GitHub personal access token (required for deployment)
        username: GitHub username (required for deployment)
        repo_name: Repository name (required for deployment)
        auto_deploy: Whether to automatically deploy to GitHub
    
    Returns:
        Dict containing project info and deployment status
    """
    
    # Generate project name if not provided
    if not project_name:
        import time
        project_name = f"generated_project_{int(time.time())}"
    
    print(f"🎯 Creating project: {project_name}")
    print(f"📝 User request: {prompt}")
    
    # Step 1: Generate project files
    agent_result = get_data_from_agent(prompt,img=img)
    
    if not agent_result:
        return {
            "success": False,
            "error": "Failed to generate project files",
            "project_path": None,
            "website_url": None
        }
    
    # Step 2: Create local project structure
    success = create_project_structure(agent_result, project_name)
    
    if not success:
        return {
            "success": False,
            "error": "Failed to create local project structure",
            "project_path": None,
            "website_url": None
        }
    
    # Determine entry HTML file (fallback to index.html)
    entry_html = agent_result.get('files', {}).get('html', {}).get('fileDir', 'index.html')

    result = {
        "success": True,
        "project_path": os.path.abspath(project_name),
        "amplified_requirements": agent_result.get('amplified_requirements', {}),
        "files_created": list(agent_result.get('files', {}).keys()),
        "website_url": None,
        "entry_html": entry_html
    }
    
    # Step 3: Deploy to GitHub if requested
    if auto_deploy and github_token and username and repo_name:
        print(f"\n🌐 Auto-deploying to GitHub...")
        
        website_url = deploy_to_github(project_name, github_token, username, repo_name)
        
        if website_url:
            result["website_url"] = website_url
            result["deployment_status"] = "success"
            print(f"\n🎉 Project successfully deployed!")
            print(f"🔗 Live website: {website_url}")
        else:
            result["deployment_status"] = "failed"
            print(f"\n⚠️ Local project created but deployment failed")
    
    elif auto_deploy:
        result["deployment_status"] = "skipped"
        result["error"] = "Missing GitHub credentials for deployment"
        print(f"\n⚠️ Deployment skipped: Missing GitHub token, username, or repo name")
    
    return result


# Simple main function for easy usage
def main():
    """Main function for command line usage"""
    
    # Configuration - Update these with your GitHub details
    GITHUB_TOKEN = "Your-token-here"  # Replace with your token
    GITHUB_USERNAME = "psudeoR3BEL"        # Replace with your username
    
    # Get user input
    isImg = input('Do you wanna give image input(y/n)?:- ')
    if isImg == 'y':
        imgPath = input('Enter the image path')
    else:
        imgPath = None     
    user_prompt = input("🎯 Describe the project you want to create: ")
    project_name = input("📁 Project name (press Enter for auto-generated): ").strip()
    
    if not project_name:
        import time
        project_name = f"ai_project_{int(time.time())}"
    
    # Ask about deployment
    deploy_choice = input("🚀 Deploy to GitHub? (y/n): ").lower().strip()
    auto_deploy = deploy_choice in ['y', 'yes', '1', 'true']
    
    repo_name = None
    if auto_deploy:
        repo_name = input(f"📦 Repository name (default: {project_name}): ").strip()
        if not repo_name:
            repo_name = project_name
    
    # Create and optionally deploy
    result = create_and_deploy_project(
        prompt=user_prompt,
        project_name=project_name,
        github_token=GITHUB_TOKEN if auto_deploy else None,
        username=GITHUB_USERNAME if auto_deploy else None,
        repo_name=repo_name,
        auto_deploy=auto_deploy,
        img=imgPath
    )
    
    # Show results
    if result["success"]:
        print(f"\n🎉 SUCCESS!")
        print(f"📂 Local project: {result['project_path']}")
        
        if result.get("website_url"):
            print(f"🌐 Live website: {result['website_url']}")
            print(f"   Note: It may take a few minutes for GitHub Pages to be fully available")
        
        # Show amplified features
        if result.get('amplified_requirements'):
            analysis = result['amplified_requirements'].get('project_analysis', {})
            features = analysis.get('key_features', [])
            if features:
                print(f"\n✨ Enhanced features added:")
                for feature in features[:5]:  # Show first 5 features
                    print(f"   • {feature}")
    else:
        print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()