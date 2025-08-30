from google import genai
from google.genai import types
from typing import Dict, Any, Optional
import json
import logging
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_data_from_agent(prompt, img=None) -> Optional[Dict[str, Dict[str, str]]]:
    """Fetch data from agent using amplification + unified development approach"""
    try:
        # Initialize client from environment variable to avoid hardcoding secrets
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("Missing GOOGLE_API_KEY environment variable")
            return None
        client = genai.Client(api_key=api_key)

        # Step 1: Amplification prompt to extract detailed requirements
        amplification_prompt = """
You are a senior web developer and UI/UX designer. Analyze the user's request and any uploaded images to create comprehensive web development requirements.

If an image is uploaded: Replicate the exact design, layout, colors, typography, spacing, and visual elements shown in the image.

Your task: Return ONLY a JSON object with this structure:

{
  "structural_demand": {
    "purpose": "What the webpage/app achieves",
    "layout": "Detailed HTML structure, sections, components needed",
    "content": "Text content, headings, labels, placeholder text",
    "semantic_structure": "HTML5 semantic elements, accessibility considerations"
  },
  "styling_demand": {
    "visual_design": "Colors, typography, spacing, visual hierarchy",
    "responsive_design": "Mobile, tablet, desktop layout requirements",
    "animations": "Hover effects, transitions, micro-interactions",
    "design_system": "Consistent spacing, color palette, component styles"
  },
  "scripting_demand": {
    "interactions": "Button clicks, form handling, user interactions",
    "dynamic_content": "Content that changes based on user actions",
    "api_integration": "Data fetching, form submissions, external services",
    "functionality": "Core features, logic, state management needed"
    import re

  }
}

Instructions:
- Be specific and detailed in each section
- If replicating an image, describe exact visual elements, spacing, and layout
- Anticipate user needs they haven't explicitly mentioned
- Focus on creating a complete, functional web experience

        """
        if img:
            my_file = client.files.upload(file=img)
            amplification_response = client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=amplification_prompt
                ),
                contents=[my_file,prompt]
            )
        else:
            # Get comprehensive requirements analysis
            amplification_response = client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    system_instruction=amplification_prompt
                ),
                contents=prompt
            )
        
        # Parse amplification response
        try:
            amplified_requirements = json.loads(amplification_response.text[7:-3])
        except json.JSONDecodeError:
            amplified_requirements = extract_json_from_response(amplification_response.text)
        
        print("📋 Amplified Requirements:")
        print(f"Structural Demand: {amplified_requirements.get('structural_demand', 'Not specified')}")
        print(f"styling_demand: {amplified_requirements.get('styling_demand', [])}")
        print(f"scripting_demand: {amplified_requirements.get('scripting_demand', [])}")
        
        # Step 2: Unified development prompt with full context
        unified_development_prompt = """
        You are a senior full-stack developer. Create a complete, production-ready web project based on the comprehensive requirements provided.
        
        IMPORTANT LINKING REQUIREMENTS:
        - HTML must reference CSS files with correct relative paths
        - HTML must reference JS files with correct relative paths  
        - Use the recommended project structure from the requirements
        - Ensure all files work together seamlessly
        
        DEVELOPMENT STANDARDS:
        - Write clean, semantic HTML5
        - Create modern, responsive CSS (use Flexbox/Grid)
        - Write vanilla JavaScript with ES6+ features
        - Include proper error handling and validation
        - Add accessibility features (ARIA labels, semantic elements)
        - Ensure cross-browser compatibility
        
        Return ONLY a JSON object with exactly this structure:
        {
            "html": {
                "fileDir": "complete/relative/path/to/file.html",
                "content": "complete HTML code with proper CSS and JS links, semantic structure, and accessibility features"
            },
            "css": {
                "fileDir": "complete/relative/path/to/file.css", 
                "content": "complete CSS code with modern styling, responsive design, and animations that matches HTML classes/ids"
            },
            "js": {
                "fileDir": "complete/relative/path/to/file.js",
                "content": "complete JavaScript code with all functionality, error handling, and DOM manipulation that works with HTML elements"
            }
        }
        
        Do not include any explanations or text outside the JSON.
        Create a fully functional, complete project that exceeds user expectations.
        """

        # Combine original prompt with amplified requirements for full context
        full_context = f"""
        
        AMPLIFIED REQUIREMENTS AND ANALYSIS:
        {json.dumps(amplified_requirements, indent=2)}
        
        Based on both the original request and the detailed analysis above, create a complete web project.
        """

        # Get the complete project files
        development_response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=unified_development_prompt
            ),
            contents=full_context
        )

        # Parse the development response
        try:
            result = json.loads(development_response.text[7:-3])
        except Exception as e:
            print(e)
            print(development_response.text)
            result = extract_json_from_response(development_response.text)
        
        # Validate the structure
        if not validate_agent_response(result):
            logger.error("Invalid response structure from development agent")
            return None
            
        print("\n🔧 Development Agent Response:")
        for file_type, file_info in result.items():
            print(f"{file_type.upper()}: {file_info.get('fileDir', 'No path')}")
            print(f"Content length: {len(file_info.get('content', ''))} characters")

        # Return both amplified requirements and files for reference
        return {
            "amplified_requirements": amplified_requirements,
            "files": result
        }
        
    except Exception as e:
        logger.error(f"Error in get_data_from_agent: {str(e)}")
        return None


def validate_agent_response(response: Dict) -> bool:
    """Validate that the agent response has the correct structure"""
    required_keys = ['html', 'css', 'js']
    
    if not isinstance(response, dict):
        return False
        
    for key in required_keys:
        if key not in response:
            logger.error(f"Missing required key: {key}")
            return False
            
        file_info = response[key]
        if not isinstance(file_info, dict):
            logger.error(f"Invalid structure for {key}")
            return False
            
        if 'fileDir' not in file_info or 'content' not in file_info:
            logger.error(f"Missing fileDir or content in {key}")
            return False
            
        # Enhanced validation checks
        content = file_info['content']
        if len(content.strip()) < 50:  # Basic content length check
            logger.warning(f"{key} content seems too short: {len(content)} characters")
            
        # Check for proper linking in HTML
        if key == 'html':
            html_content = file_info['content'].lower()
            has_css_link = 'stylesheet' in html_content or 'link' in html_content
            has_js_link = 'script' in html_content
            
            if not has_css_link:
                logger.warning("HTML might not be properly linked to CSS")
            if not has_js_link:
                logger.warning("HTML might not be properly linked to JS")
                
        # Check CSS has actual styles
        elif key == 'css':
            css_content = file_info['content']
            if '{' not in css_content or '}' not in css_content:
                logger.warning("CSS content might be malformed")
                
        # Check JS has actual code
        elif key == 'js':
            js_content = file_info['content']
            if 'function' not in js_content and 'const' not in js_content and 'let' not in js_content:
                logger.warning("JavaScript content might be incomplete")
    
    return True
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


def extract_json_from_response(response_text: str) -> Dict[str, Dict[str, str]]:
    """Extract JSON from response that might contain extra text"""
    try:
        import re
        # Look for JSON object pattern - more robust regex
        json_pattern = r'\{(?:[^{}]|{[^{}]*})*\}'
        matches = re.findall(json_pattern, response_text, re.DOTALL)
        
        for match in matches:
            try:
                parsed = json.loads(match)
                # Check if it has the expected structure for amplification
                if 'project_analysis' in parsed and 'detailed_requirements' in parsed:
                    return parsed
                # New amplification shape
                if all(k in parsed for k in ['structural_demand', 'styling_demand', 'scripting_demand']):
                    return parsed
                # Check if it has the expected structure for development
                elif all(key in parsed for key in ['html', 'css', 'js']):
                    return parsed
            except json.JSONDecodeError:
                continue
                
        # If no valid JSON found, create a fallback structure
        logger.warning("No valid JSON found, creating fallback structure")
        return create_fallback_structure(response_text)
        
    except Exception as e:
        logger.error(f"Error extracting JSON: {str(e)}")
        return create_fallback_structure(response_text)