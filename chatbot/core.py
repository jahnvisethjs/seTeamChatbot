import os
from typing import List, Dict, Any, Optional
from chatbot.rag_engine import RAGEngine
from chatbot.dev_setup import DevSetupAssistant
from chatbot.onboarding_assistant import OnboardingAssistant
from config.settings import KNOWLEDGE_BASE_DIR, ASU_AI_API_TOKEN

class MegaChatbot:
    def __init__(self):
        self.rag_engine = RAGEngine()
        self.dev_setup_assistant = DevSetupAssistant()
        self.onboarding_assistant = OnboardingAssistant(self.rag_engine)
        self.conversation_history = []
        self.current_mode = "general"  # "general", "dev_setup", "onboarding"
        self.step_by_step_active = False  # Only True when user opts into guided steps
        self.initialize_knowledge_base()
    
    def initialize_knowledge_base(self) -> None:
        """Initialize the knowledge base with documents."""
        # Ensure knowledge base directory exists
        os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
        
        # Load documents from knowledge base
        # Load documents from knowledge base
        self.rag_engine.load_documents(KNOWLEDGE_BASE_DIR)
        
        # Load onboarding agendas
        onboarding_agendas_dir = os.path.join("data", "onboarding_agendas")
        if os.path.exists(onboarding_agendas_dir):
            self.rag_engine.load_documents(onboarding_agendas_dir)
            
        self.rag_engine.create_vectorstore()
    
    def process_message(self, message: str, mode: str = None, image_bytes: Optional[bytes] = None) -> str:
        """Process a user message and return a response."""
        if mode:
            self.current_mode = mode
        
        # Add message to history (content is text for history)
        self.conversation_history.append({"role": "user", "content": message})
        
        # Process based on current mode
        if self.current_mode == "dev_setup":
            response = self.handle_dev_setup_message(message)
        elif self.current_mode == "onboarding":
            response = self.handle_onboarding_message(message, image_bytes)
        else:
            response = self.handle_general_message(message, image_bytes)
        
        # Add response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Keep history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return response
    
    def handle_general_message(self, message: str, image_bytes: Optional[bytes] = None) -> str:
        """Handle general chat messages, optionally with an image attachment."""
        # If an image is attached, use vision to analyze it
        if image_bytes:
            return self._handle_image_query(message, image_bytes)
        
        # Check if message is about dev setup
        dev_setup_keywords = [
            "dev setup", "development setup", "environment setup",
            "install", "setup", "configuration", "prerequisites"
        ]
        
        if any(keyword in message.lower() for keyword in dev_setup_keywords):
            self.current_mode = "dev_setup"
            return self.handle_dev_setup_message(message)
        
        # Use RAG for general questions
        if self.rag_engine.rag_chain:
            try:
                response = self.rag_engine.query(message)
                return response
            except Exception as e:
                return f"I'm having trouble processing your request. Please try rephrasing or ask about dev setup, onboarding, or general team support."
        
        return """I'm your SE Team assistant! I can help you with:

**🔧 Dev Setup**: Step-by-step guidance for setting up your development environment
**📅 Onboarding**: Help with onboarding schedules and team orientation  
**📚 Documentation**: Access to team documents, guides, and resources
**🖼️ Image Analysis**: Upload an image and ask me about it
**❓ General Support**: Answer questions about team processes and tools

What would you like help with today?"""
    
    def _handle_image_query(self, message: str, image_bytes: bytes) -> str:
        """Analyze an uploaded image and respond to the user's question about it."""
        if not self.rag_engine.llm:
            return "I need access to the AI model to analyze images. Please check your API token."
        
        import base64
        from io import BytesIO
        try:
            from PIL import Image
        except ImportError:
            Image = None
        
        # Process image — convert to PNG for maximum compatibility
        if Image:
            try:
                img = Image.open(BytesIO(image_bytes))
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                max_dim = 1024
                if max(img.width, img.height) > max_dim:
                    scale = max_dim / max(img.width, img.height)
                    new_size = (int(img.width * scale), int(img.height * scale))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                image_bytes = buffer.getvalue()
            except Exception as img_err:
                print(f"Image processing warning: {img_err}")
        
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Build text prompt
        if message.strip():
            text_prompt = f'The user uploaded an image and asked: "{message}"\n\nPlease analyze the image and respond to their question. Be helpful, detailed, and specific about what you see in the image.'
        else:
            text_prompt = "The user uploaded an image without a specific question.\n\nPlease describe what you see in the image in detail. Include relevant details like:\n- What the image shows (objects, text, diagrams, charts, etc.)\n- Any key information visible\n- Any relevant context or interpretation"
        
        try:
            response = self.rag_engine.llm.invoke_vision(text_prompt, image_base64)
            return response
        except Exception as e:
            return f"I encountered an error analyzing the image: {str(e)}\n\nPlease try uploading a smaller or clearer image, or describe what you'd like to know about it."
    
    def handle_dev_setup_message(self, message: str) -> str:
        """Handle dev setup specific messages."""
        message_lower = message.lower()
        
        # Expanded list of progression keywords
        progression_keywords = [
            "next", "continue", "move ahead", "proceed", "go ahead",
            "done", "completed", "finished", "complete", "all set",
            "ready", "got it", "working", "success", "successfully",
            "what's next", "what next", "move on", "skip", "let's go"
        ]
        
        # Check for navigation commands - NEXT
        if any(keyword in message_lower for keyword in progression_keywords):
            # Acknowledge completion and move forward
            next_step = self.dev_setup_assistant.next_step()
            if next_step:
                return f"""✅ Great! Moving to the next step.

{self.dev_setup_assistant.format_current_step()}"""
            else:
                return "🎉 Congratulations! You've completed the dev setup guide. Your development environment should now be ready!"
        
        elif "previous" in message_lower or "back" in message_lower or "go back" in message_lower:
            prev_step = self.dev_setup_assistant.previous_step()
            if prev_step:
                return self.dev_setup_assistant.format_current_step()
            else:
                return "You're at the beginning of the setup guide."
        
        elif "start" in message_lower or "begin" in message_lower or "reset" in message_lower:
            self.dev_setup_assistant.reset_progress()
            return f"""🚀 Starting Dev Setup Guide!

{self.dev_setup_assistant.format_current_step()}

**Navigation:**
- Say "next", "done", or "move ahead" to continue
- Say "previous" or "back" to go back
- Say "error" followed by your error message for help
- Say "status" to see your progress"""
        
        elif "status" in message_lower or "progress" in message_lower:
            progress = self.dev_setup_assistant.get_step_progress()
            return f"""📊 **Setup Progress:**
- Current Step: {progress['current_step']} of {progress['total_steps']}
- Progress: {progress['percentage']:.1f}%

{self.dev_setup_assistant.format_current_step()}"""
        
        elif message_lower == "help":
            return f"""🔧 **Dev Setup Assistant Help:**

You can chat naturally with me! For example:
- Say **"step by step"** to start the guided installation walkthrough
- Ask any question about the dev setup (e.g., "What is Colima?")
- Describe errors you're encountering and I'll help troubleshoot

**During step-by-step mode:** `next`, `back`, `status`, `start`"""
        
        # LLM-first: send everything through the LLM for understanding
        return self.dev_setup_assistant.process_with_llm(message, self.conversation_history)
    
    def handle_onboarding_message(self, message: str, image_bytes: Optional[bytes] = None) -> str:
        """Handle onboarding specific messages."""
        return self.onboarding_assistant.process_message(message, image_bytes)
    
    def get_available_modes(self) -> List[str]:
        """Get list of available modes."""
        return ["general", "dev_setup", "onboarding"]
    
    def switch_mode(self, mode: str) -> str:
        """Switch to a different mode."""
        if mode in self.get_available_modes():
            self.current_mode = mode
            self.step_by_step_active = False
            if mode == "dev_setup":
                return """🔧 **Welcome to Dev Setup Mode!**

How would you like to get started?

1. 📋 **Step-by-step installation** — I'll walk you through the full setup guide one step at a time. Just say **"step by step"**.
2. ❓ **Ask a question** — If you already know what you need help with, just ask! (e.g., "How do I set up Docker?" or "I'm getting a port conflict error.")

What would you like to do?"""
            elif mode == "onboarding":
                return self.handle_onboarding_message("")
            else:
                return "Switched to general chat mode. How can I help you?"
        else:
            return f"Unknown mode: {mode}. Available modes: {', '.join(self.get_available_modes())}"
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation."""
        if not self.conversation_history:
            return "No conversation history yet."
        
        user_messages = [msg["content"] for msg in self.conversation_history if msg["role"] == "user"]
        return f"Conversation summary: {len(user_messages)} user messages, current mode: {self.current_mode}" 