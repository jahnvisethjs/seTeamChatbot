import os
import re
from typing import List, Dict, Any
import markdown
from pathlib import Path

def ensure_directory_exists(directory_path: str) -> None:
    """Ensure a directory exists, create if it doesn't."""
    Path(directory_path).mkdir(parents=True, exist_ok=True)

def load_markdown_file(file_path: str) -> str:
    """Load and return the content of a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return ""

def save_markdown_file(file_path: str, content: str) -> None:
    """Save content to a markdown file."""
    ensure_directory_exists(os.path.dirname(file_path))
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def extract_steps_from_markdown(content: str) -> List[Dict[str, Any]]:
    """Extract numbered steps from markdown content."""
    steps = []
    lines = content.split('\n')
    current_step = None
    in_code_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # Track code block fences
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue  # Skip the fence lines themselves
        
        # Inside a code block — capture as commands
        if in_code_block and current_step:
            if stripped:
                current_step['commands'].append(stripped)
            continue
        
        # Match numbered steps (1., 2., etc.)
        step_match = re.match(r'^(\d+)\.\s+(.+)$', stripped)
        if step_match:
            if current_step:
                steps.append(current_step)
            current_step = {
                'number': int(step_match.group(1)),
                'title': step_match.group(2),
                'content': [],
                'commands': [],
                'checks': []
            }
        elif current_step and stripped:
            # Look for check items (lines with [ ] or [x])
            if re.match(r'^[-*]\s*\[[ x]\]', stripped):
                current_step['checks'].append(stripped)
            else:
                current_step['content'].append(stripped)
    
    if current_step:
        steps.append(current_step)
    
    return steps

def format_step_for_display(step: Dict[str, Any]) -> str:
    """Format a step for display in the UI."""
    formatted = f"**Step {step['number']}: {step['title']}**\n\n"
    
    if step['content']:
        formatted += "\n".join(step['content']) + "\n\n"
    
    if step['commands']:
        formatted += "**Commands to run:**\n```bash\n"
        formatted += "\n".join(step['commands'])
        formatted += "\n```\n\n"
    
    if step['checks']:
        formatted += "**Verification checks:**\n"
        for check in step['checks']:
            formatted += f"- {check}\n"
    
    return formatted

def detect_error_in_response(response: str) -> bool:
    """Detect if a response contains error indicators."""
    error_indicators = [
        'error', 'failed', 'not found', 'permission denied',
        'command not found', 'cannot', 'unable', 'failed to',
        'error:', 'exception', 'traceback'
    ]
    
    response_lower = response.lower()
    return any(indicator in response_lower for indicator in error_indicators)

def clean_text(text: str) -> str:
    """Clean and normalize text for processing."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove markdown code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Remove inline code
    text = re.sub(r'`.*?`', '', text)
    return text.strip() 