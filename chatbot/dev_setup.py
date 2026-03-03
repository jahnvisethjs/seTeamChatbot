import os
from typing import List, Dict, Any, Optional
from chatbot.utils import (
    load_markdown_file, extract_steps_from_markdown, 
    format_step_for_display
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
    
    def process_with_llm(self, message: str, conversation_history: list) -> str:
        """
        Use the LLM to understand the user's message in the context of the dev setup guide.
        The LLM classifies intent AND generates a helpful response in one call.
        Returns the response to show the user.
        """
        # Build current step context
        current_step = self.get_current_step()
        if current_step:
            step_context = f"Step {current_step['number']}: {current_step['title']}"
            step_detail = self.format_current_step()
        else:
            step_context = "No steps loaded"
            step_detail = "No step information available."
        
        progress = self.get_step_progress()
        
        # Build recent conversation context (last 6 messages)
        recent_context = ""
        if conversation_history:
            recent_messages = conversation_history[-6:]
            recent_context = "\n".join([
                f"{msg['role'].upper()}: {msg['content'][:200]}"
                for msg in recent_messages
            ])
        
        # Load the full dev setup guide for context
        guide_content = load_markdown_file(DEV_SETUP_GUIDE)
        if not guide_content:
            guide_content = "No dev setup guide available."
        
        # Load FAQ for error context
        faq_content = load_markdown_file(FAQ_FILE)
        if not faq_content:
            faq_content = "No FAQ available."
        
        prompt = f"""You are a helpful Dev Setup Assistant guiding a user through setting up their development environment.

CURRENT STATE:
- Current Step: {step_context}
- Progress: Step {progress['current_step']} of {progress['total_steps']} ({progress['percentage']:.0f}%)

CURRENT STEP DETAILS:
{step_detail}

DEV SETUP GUIDE (full reference):
{guide_content}

COMMON ERRORS & SOLUTIONS:
{faq_content}

RECENT CONVERSATION:
{recent_context}

USER MESSAGE: "{message}"

INSTRUCTIONS:
1. Understand what the user is saying in the context of the dev setup process.
2. ONLY include [ACTION: NEXT] if the user EXPLICITLY says they completed the current step or want to move to the next one (e.g., "done", "I finished this step", "move on"). NEVER include it if the user is asking a question, even if they mention being done with other steps.
3. If the user asks about a SPECIFIC step by number (e.g., "help me with step 10"), answer using the full dev setup guide above. Do NOT advance the step — just answer the question.
4. If the user wants to go back to a previous step, include [ACTION: BACK] at the very end.
5. If the user wants to restart, include [ACTION: RESET] at the very end.
6. If the user is asking a question, answer it using the dev setup guide and FAQ content above. Do NOT include any [ACTION: ...] tag.
7. If the user reports an error, provide specific troubleshooting advice from the FAQ and guide. Do NOT include any [ACTION: ...] tag.

Respond naturally and helpfully. Be concise but informative. Use markdown formatting."""

        try:
            response = self.rag_engine.direct_query(prompt)
            
            # Parse action tags from the response
            action = None
            if "[ACTION: NEXT]" in response:
                action = "next"
                response = response.replace("[ACTION: NEXT]", "").strip()
            elif "[ACTION: BACK]" in response:
                action = "back"
                response = response.replace("[ACTION: BACK]", "").strip()
            elif "[ACTION: RESET]" in response:
                action = "reset"
                response = response.replace("[ACTION: RESET]", "").strip()
            
            # Perform the navigation action
            if action == "next":
                next_step = self.next_step()
                if next_step:
                    response += f"\n\n---\n📍 **Next Step:**\n{self.format_current_step()}"
                else:
                    response += "\n\n🎉 **Congratulations! You've completed all steps in the dev setup guide!**"
            elif action == "back":
                prev_step = self.previous_step()
                if prev_step:
                    response += f"\n\n---\n📍 **Previous Step:**\n{self.format_current_step()}"
                else:
                    response += "\n\n⚠️ You're already at the first step."
            elif action == "reset":
                self.reset_progress()
                response += f"\n\n---\n📍 **Starting from the beginning:**\n{self.format_current_step()}"
            
            return response
            
        except Exception as e:
            # Fallback: return current step info with the error
            return f"""I had trouble processing your message, but here's where you are:

{self.format_current_step()}

**Quick Commands:** Say "next" to advance, "back" to go back, or ask me any question about the setup process.

_(Error: {str(e)})_"""
    
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