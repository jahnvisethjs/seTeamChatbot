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
    current_code_lang = ""
    current_code_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Track code block fences
        if stripped.startswith('```'):
            if not in_code_block:
                # Opening fence — capture language tag
                in_code_block = True
                current_code_lang = stripped[3:].strip() or "bash"
                current_code_lines = []
            else:
                # Closing fence — save the code block
                in_code_block = False
                if current_step and current_code_lines:
                    current_step['code_blocks'].append({
                        'lang': current_code_lang,
                        'lines': list(current_code_lines)
                    })
                    # Also add to commands for backward compatibility
                    current_step['commands'].extend(current_code_lines)
                current_code_lines = []
                current_code_lang = ""
            continue
        
        # Inside a code block — capture lines
        if in_code_block:
            if stripped:
                current_code_lines.append(stripped)
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
                'code_blocks': [],
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
    """Format a step for display in the UI with proper markdown code blocks."""
    formatted = f"**Step {step['number']}: {step['title']}**\n\n"
    
    if step['content']:
        formatted += "\n".join(step['content']) + "\n\n"
    
    # Use preserved code blocks with their original language tags
    code_blocks = step.get('code_blocks', [])
    if code_blocks:
        formatted += "**Commands to run:**\n"
        for block in code_blocks:
            lang = block.get('lang', 'bash')
            formatted += f"```{lang}\n"
            formatted += "\n".join(block['lines'])
            formatted += "\n```\n\n"
    elif step['commands']:
        # Fallback for steps without code_blocks (backward compatibility)
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