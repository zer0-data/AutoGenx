
import base64
import requests
import logging
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def delete_repo_contents(github_token: str, username: str, repo_name: str, path: str = "") -> bool:
    """Delete all contents of a GitHub repository recursively"""
    try:
        contents_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{path}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(contents_url, headers=headers)
        response.raise_for_status()
        
        contents = response.json()
        
        if not contents:
            logger.info(f"Path {path} is empty")
            return True
            
        if not isinstance(contents, list):
            contents = [contents]
            
        for item in contents:
            item_path = item['path']
            
            if item['type'] == 'dir':
                if not delete_repo_contents(github_token, username, repo_name, item_path):
                    return False
            else:
                delete_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{item_path}"
                delete_data = {
                    "message": f"Delete {item_path}",
                    "sha": item['sha'],
                    "branch": "main"
                }
                
                delete_response = requests.delete(delete_url, json=delete_data, headers=headers)
                delete_response.raise_for_status()
                logger.info(f"Deleted {item_path}")
            
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error deleting repository contents: {str(e)}")
        return False

def create_github_repo(github_token: str, username: str, repo_name: str) -> bool:
    """Create GitHub repository if it doesn't exist"""
    try:
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
        response = requests.get(repo_url, headers=headers)
        
        if response.status_code == 404:
            create_url = "https://api.github.com/user/repos"
            repo_data = {
                "name": repo_name,
                "private": False,
                "auto_init": True
            }
            response = requests.post(create_url, json=repo_data, headers=headers)
            response.raise_for_status()
            logger.info(f"Created new repository: {repo_name}")
        else:
            logger.info(f"Repository {repo_name} already exists")
        
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating repository: {str(e)}")
        return False

def handle_file_upload(local_file_path: str, repo_path: str, github_token: str, username: str, repo_name: str) -> bool:
    """Upload a single file to the repository"""
    try:
        content_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{repo_path}"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        with open(local_file_path, "rb") as file:
            file_content = base64.b64encode(file.read()).decode("utf-8")
            
        file_data = {
            "message": f"Upload {repo_path}",
            "content": file_content,
            "branch": "main"
        }
        
        response = requests.put(content_url, json=file_data, headers=headers)
        response.raise_for_status()
        
        logger.info(f"✅ File '{repo_path}' uploaded successfully!")
        return True
        
    except Exception as e:
        logger.error(f"⚠️ Error uploading file {local_file_path}: {str(e)}")
        return False

def host_multi_files(dir_name: str, github_token: str, username: str, repo_name: str, current_path: str = "") -> bool:
    """Upload multiple files maintaining directory structure"""
    try:
        if not current_path:
            if not create_github_repo(github_token, username, repo_name):
                return False
            if not delete_repo_contents(github_token, username, repo_name):
                return False
            logger.info("Repository cleaned and ready for upload")
        
        if not os.path.exists(dir_name):
            logger.error(f"Directory {dir_name} does not exist")
            return False
            
        for item in os.listdir(dir_name):
            full_path = os.path.join(dir_name, item)
            repo_path = os.path.join(current_path, item).replace("\\", "/")
            
            if os.path.isfile(full_path):
                if not handle_file_upload(full_path, repo_path, github_token, username, repo_name):
                    logger.error(f"Failed to upload {repo_path}")
            else:
                if not host_multi_files(full_path, github_token, username, repo_name, repo_path):
                    return False
                
        return True
        
    except Exception as e:
        logger.error(f"Error processing directory {dir_name}: {str(e)}")
        return False

def enable_github_pages(github_token: str, username: str, repo_name: str) -> str:
    """Enable GitHub Pages for the repository"""
    try:
        pages_api_url = f"https://api.github.com/repos/{username}/{repo_name}/pages"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        pages_data = {
            "source": {
                "branch": "main",
                "path": "/"
            }
        }
        
        response = requests.post(pages_api_url, json=pages_data, headers=headers)
        
        if response.status_code in [201, 204, 409]:
            website_url = f"https://{username}.github.io/{repo_name}/"
            print(f"✅ GitHub Pages enabled for {repo_name}!")
            print(f"🔗 Your website will be available soon at: {website_url}")
            return website_url
        else:
            print(f"⚠️ Error enabling GitHub Pages: {response.json()}")
            return False
            
    except Exception as e:
        logger.error(f"Error enabling GitHub Pages: {str(e)}")
        return False

def deploy_to_github(project_path: str, github_token: str, username: str, repo_name: str) -> str:
    """Deploy project to GitHub and enable Pages"""
    try:
        print(f"\n🚀 Deploying project to GitHub...")
        print(f"   Repository: {username}/{repo_name}")
        print(f"   Local path: {project_path}")
        
        # Upload files
        success = host_multi_files(project_path, github_token, username, repo_name)
        
        if success:
            print("✅ All files uploaded successfully!")
            
            # Enable GitHub Pages
            website_url = enable_github_pages(github_token, username, repo_name)
            
            if website_url:
                return website_url
            else:
                print("⚠️ Files uploaded but GitHub Pages setup failed")
                return f"https://github.com/{username}/{repo_name}"
        else:
            print("⚠️ Some errors occurred during upload")
            return False
            
    except Exception as e:
        logger.error(f"Error in deploy_to_github: {str(e)}")
        return False
