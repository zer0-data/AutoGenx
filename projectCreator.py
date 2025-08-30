import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_fallback_structure(response_text: str) -> Dict[str, Dict[str, str]]:
    """Create a fallback structure when JSON parsing fails"""
    return {
        "html": {
            "fileDir": "index.html",
            "content": f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Project</title>
    <link rel="stylesheet" href="styles/style.css">
</head>
<body>
    <div class="container">
        <h1>Generated Project</h1>
        <p>Content generated from: {response_text[:200]}...</p>
    </div>
    <script src="scripts/script.js"></script>
</body>
</html>"""
        },
        "css": {
            "fileDir": "styles/style.css", 
            "content": """/* Generated CSS */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: Arial, sans-serif;
}

h1 {
    color: #333;
    text-align: center;
}

p {
    line-height: 1.6;
    color: #666;
}"""
        },
        "js": {
            "fileDir": "scripts/script.js",
            "content": """// Generated JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Project loaded successfully');
    
    // Basic functionality
    const container = document.querySelector('.container');
    if (container) {
        container.addEventListener('click', function() {
            console.log('Container clicked');
        });
    }
});"""
        }
    }


def create_project_structure(agent_result: Dict[str, Any], project_name: str = "testProject") -> bool:
    """
    Create project structure from the agent result with amplified requirements
    
    Args:
        agent_result: Result from get_data_from_agent containing amplified requirements and files
        project_name: Name of the project directory (default: 'testProject')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f'🚀 Creating project structure for: {project_name}')
        
        # Create main project directory
        project_path = Path(project_name)
        if not project_path.exists():
            project_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created project directory: {project_name}")
        
        # Extract files data from agent result
        files_data = agent_result.get('files', {})
        
        # Process each file type (html, css, js)
        created_files = []
        for file_type, file_info in files_data.items():
            if isinstance(file_info, dict) and 'fileDir' in file_info and 'content' in file_info:
                file_dir = file_info['fileDir']
                content = file_info['content']
                
                # Create full path relative to project directory
                full_file_path = project_path / file_dir
                
                # Create parent directories if they don't exist
                full_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file content
                with open(full_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"Created {file_type} file: {full_file_path}")
                created_files.append(f"{file_type}: {file_dir}")
                print(f"✅ Created {file_type.upper()}: {file_dir}")
            else:
                logger.warning(f"Invalid file structure for {file_type}: {file_info}")
        
        # Create project documentation with amplified requirements
        if 'amplified_requirements' in agent_result:
            requirements_path = project_path / "PROJECT_REQUIREMENTS.md"
            with open(requirements_path, 'w', encoding='utf-8') as f:
                f.write(generate_project_documentation(agent_result['amplified_requirements']))
            print("📄 Created PROJECT_REQUIREMENTS.md")
        
        print(f"\n🎉 Project '{project_name}' created successfully!")
        print(f"📁 Files created: {len(created_files)}")
        for file_info in created_files:
            print(f"   • {file_info}")
            
        return True
        
    except Exception as e:
        logger.error(f"Error creating project structure: {str(e)}")
        return False


def generate_project_documentation(requirements: Dict) -> str:
    """Generate project documentation from amplified requirements (supports multiple shapes)."""
    # Support legacy shape
    if 'project_analysis' in requirements or 'detailed_requirements' in requirements:
        analysis = requirements.get('project_analysis', {})
        detailed = requirements.get('detailed_requirements', {})
        doc = f"""# Project Requirements and Analysis

## Core Purpose
{analysis.get('core_purpose', 'Not specified')}

## Target Users
{analysis.get('target_users', 'Not specified')}

## Key Features
"""
        for feature in analysis.get('key_features', []):
            doc += f"- {feature}\n"
        doc += "\n## Technical Requirements\n"
        for req in analysis.get('technical_requirements', []):
            doc += f"- {req}\n"
        doc += f"""
\n## UI/UX Considerations
{analysis.get('ui_ux_considerations', 'Not specified')}

## Detailed Implementation Requirements

### HTML Structure
{detailed.get('html_structure', 'Not specified')}

### CSS Styling
{detailed.get('css_styling', 'Not specified')}

### JavaScript Functionality
{detailed.get('js_functionality', 'Not specified')}

---
*Generated automatically from user requirements*
"""
        return doc

    # Support new shape from current amplification prompt
    structural = requirements.get('structural_demand', {})
    styling = requirements.get('styling_demand', {})
    scripting = requirements.get('scripting_demand', {})

    doc = "# Project Requirements and Analysis\n\n"
    doc += "## Structural Demand\n"
    for k in ["purpose", "layout", "content", "semantic_structure"]:
        doc += f"- {k.replace('_',' ').title()}: {structural.get(k, 'Not specified')}\n"

    doc += "\n## Styling Demand\n"
    for k in ["visual_design", "responsive_design", "animations", "design_system"]:
        doc += f"- {k.replace('_',' ').title()}: {styling.get(k, 'Not specified')}\n"

    doc += "\n## Scripting Demand\n"
    for k in ["interactions", "dynamic_content", "api_integration", "functionality"]:
        doc += f"- {k.replace('_',' ').title()}: {scripting.get(k, 'Not specified')}\n"

    doc += "\n---\n*Generated automatically from user requirements*\n"
    return doc
