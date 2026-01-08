import os
from typing import List, Dict, Any, Optional
from chatbot.utils import (
    load_markdown_file, extract_steps_from_markdown, 
    format_step_for_display, detect_error_in_response
)
from chatbot.rag_engine import RAGEngine
from config.settings import DEV_SETUP_GUIDE, FAQ_FILE

class DevSetupAssistant:
    def __init__(self):
        self.current_step = 0
        self.total_steps = 0
        self.steps = []
        self.progress = {}
        self.rag_engine = RAGEngine()
        self.load_dev_setup_guide()
        
    def load_dev_setup_guide(self) -> None:
        """Load the dev setup guide and extract steps."""
        content = load_markdown_file(DEV_SETUP_GUIDE)
        if content:
            self.steps = extract_steps_from_markdown(content)
            self.total_steps = len(self.steps)
        else:
            # Create a default dev setup guide if none exists
            self.create_default_dev_setup_guide()
            self.load_dev_setup_guide()
    
    def create_default_dev_setup_guide(self) -> None:
        """Create a default dev setup guide."""
        default_guide = """# Development Environment Setup Guide

## Prerequisites
1. **Install Git**
   - Download Git from https://git-scm.com/
   - Verify installation: `git --version`
   - [ ] Git is installed and accessible

2. **Install Python**
   - Download Python 3.8+ from https://python.org/
   - Verify installation: `python --version`
   - [ ] Python is installed and accessible

3. **Install Node.js**
   - Download Node.js from https://nodejs.org/
   - Verify installation: `node --version` and `npm --version`
   - [ ] Node.js and npm are installed

4. **Install Docker**
   - Download Docker Desktop from https://docker.com/
   - Verify installation: `docker --version`
   - [ ] Docker is installed and running

5. **Setup IDE**
   - Install VS Code or your preferred IDE
   - Install recommended extensions
   - [ ] IDE is configured

6. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```
   - [ ] Repository is cloned locally

7. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   npm install
   ```
   - [ ] All dependencies are installed

8. **Environment Configuration**
   - Copy `.env.example` to `.env`
   - Fill in required environment variables
   - [ ] Environment is configured

9. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
   - [ ] Database is initialized

10. **Run Development Server**
    ```bash
    python manage.py runserver
    ```
    - [ ] Server starts without errors
    - [ ] Application is accessible at http://localhost:8000

## Verification
- [ ] All services are running
- [ ] No error messages in console
- [ ] Application loads correctly
- [ ] Database connections work
- [ ] API endpoints respond
"""
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(DEV_SETUP_GUIDE), exist_ok=True)
        
        with open(DEV_SETUP_GUIDE, 'w', encoding='utf-8') as f:
            f.write(default_guide)
    
    def get_current_step(self) -> Optional[Dict[str, Any]]:
        """Get the current step information."""
        if 0 <= self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
    
    def get_step_progress(self) -> Dict[str, Any]:
        """Get current progress information."""
        return {
            'current_step': self.current_step + 1,
            'total_steps': self.total_steps,
            'percentage': (self.current_step + 1) / self.total_steps * 100 if self.total_steps > 0 else 0
        }
    
    def next_step(self) -> Optional[Dict[str, Any]]:
        """Move to the next step."""
        if self.current_step < len(self.steps) - 1:
            self.current_step += 1
            return self.get_current_step()
        return None
    
    def previous_step(self) -> Optional[Dict[str, Any]]:
        """Move to the previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            return self.get_current_step()
        return None
    
    def go_to_step(self, step_number: int) -> Optional[Dict[str, Any]]:
        """Go to a specific step."""
        if 0 <= step_number < len(self.steps):
            self.current_step = step_number
            return self.get_current_step()
        return None
    
    def format_current_step(self) -> str:
        """Format the current step for display."""
        step = self.get_current_step()
        if step:
            return format_step_for_display(step)
        return "No steps available."
    
    def handle_error_response(self, error_message: str) -> str:
        """Handle error responses and provide solutions."""
        # Load FAQ for error resolution
        faq_content = load_markdown_file(FAQ_FILE)
        if not faq_content:
            self.create_default_faq()
            faq_content = load_markdown_file(FAQ_FILE)
        
        # Use RAG to find relevant solutions
        self.rag_engine.load_documents(os.path.dirname(FAQ_FILE))
        self.rag_engine.create_vectorstore()
        
        # Search for relevant error solutions
        similar_docs = self.rag_engine.similarity_search(error_message, k=2)
        
        if similar_docs:
            # Use RAG to generate a response
            response = self.rag_engine.query(f"Error: {error_message}. Provide a solution based on the knowledge base.")
            return response
        else:
            # Fallback response
            return f"""I detected an error: {error_message}

**Troubleshooting Steps:**
1. Check if all prerequisites are installed
2. Verify the command syntax
3. Ensure you're in the correct directory
4. Check for permission issues
5. Try running the command with administrator privileges

**Common Solutions:**
- Restart your terminal/command prompt
- Clear any cached data
- Check if the service is running
- Verify network connectivity

If the issue persists, please provide more details about the error."""
    
    def create_default_faq(self) -> None:
        """Create a default FAQ file."""
        default_faq = """# Common Development Setup Errors and Solutions

## Git Issues
**Error: 'git' is not recognized**
- Solution: Install Git from https://git-scm.com/
- Verify PATH environment variable includes Git

**Error: Permission denied**
- Solution: Run as administrator or check file permissions
- Use `sudo` on Linux/Mac

## Python Issues
**Error: 'python' is not recognized**
- Solution: Install Python and add to PATH
- Try `python3` instead of `python`

**Error: Module not found**
- Solution: Install missing packages with `pip install package_name`
- Check virtual environment activation

## Node.js Issues
**Error: 'node' is not recognized**
- Solution: Install Node.js from https://nodejs.org/
- Restart terminal after installation

**Error: npm install fails**
- Solution: Clear npm cache: `npm cache clean --force`
- Check network connectivity
- Try using a different npm registry

## Docker Issues
**Error: Docker daemon not running**
- Solution: Start Docker Desktop
- Check if Docker service is running

**Error: Permission denied on Docker commands**
- Solution: Add user to docker group
- Run with sudo (Linux/Mac)

## Database Issues
**Error: Database connection failed**
- Solution: Check database service is running
- Verify connection settings in .env file
- Ensure database exists

## General Issues
**Error: Port already in use**
- Solution: Find and kill process using the port
- Use different port: `python manage.py runserver 8001`

**Error: File not found**
- Solution: Check current directory
- Verify file paths are correct
- Ensure files exist in expected locations
"""
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(FAQ_FILE), exist_ok=True)
        
        with open(FAQ_FILE, 'w', encoding='utf-8') as f:
            f.write(default_faq)
    
    def reset_progress(self) -> None:
        """Reset the progress and start from the beginning."""
        self.current_step = 0
        self.progress = {}
    
    def mark_step_complete(self, step_number: int) -> None:
        """Mark a step as complete."""
        self.progress[step_number] = True
    
    def is_step_complete(self, step_number: int) -> bool:
        """Check if a step is complete."""
        return self.progress.get(step_number, False) 