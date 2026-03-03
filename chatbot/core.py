import os
from typing import List, Dict, Any, Optional
from chatbot.rag_engine import RAGEngine
from chatbot.dev_setup import DevSetupAssistant
from config.settings import KNOWLEDGE_BASE_DIR, ASU_AI_API_TOKEN

class MegaChatbot:
    def __init__(self):
        self.rag_engine = RAGEngine()
        self.dev_setup_assistant = DevSetupAssistant()
        self.conversation_history = []
        self.current_mode = "general"  # "general", "dev_setup", "onboarding"
        self.step_by_step_active = False  # Only True when user opts into guided steps
        self.initialize_knowledge_base()
    
    def initialize_knowledge_base(self) -> None:
        """Initialize the knowledge base with documents."""
        # Ensure knowledge base directory exists
        os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
        
        # Load documents from knowledge base
        self.rag_engine.load_documents(KNOWLEDGE_BASE_DIR)
        self.rag_engine.create_vectorstore()
    
    def process_message(self, message: str, mode: str = None) -> str:
        """Process a user message and return a response."""
        if mode:
            self.current_mode = mode
        
        # Add message to history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Process based on current mode
        if self.current_mode == "dev_setup":
            response = self.handle_dev_setup_message(message)
        elif self.current_mode == "onboarding":
            response = self.handle_onboarding_message(message)
        else:
            response = self.handle_general_message(message)
        
        # Add response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Keep history manageable
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return response
    
    def handle_general_message(self, message: str) -> str:
        """Handle general chat messages."""
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
**❓ General Support**: Answer questions about team processes and tools

What would you like help with today?"""
    
    def handle_dev_setup_message(self, message: str) -> str:
        """Handle dev setup specific messages using LLM-first approach."""
        message_stripped = message.strip().lower()
        
        # Check if user wants to start step-by-step mode
        if message_stripped in ("start", "reset", "begin", "step by step", "step-by-step", "guided", "guided setup"):
            self.step_by_step_active = True
            self.dev_setup_assistant.reset_progress()
            return f"""🚀 **Starting Step-by-Step Dev Setup Guide!**

{self.dev_setup_assistant.format_current_step()}

Just chat naturally — tell me when you're done with a step, ask questions, or report any errors!"""
        
        # Fast-path shortcuts (only when step-by-step is active)
        if self.step_by_step_active:
            if message_stripped == "next":
                next_step = self.dev_setup_assistant.next_step()
                if next_step:
                    return f"✅ Moving to the next step.\n\n{self.dev_setup_assistant.format_current_step()}"
                else:
                    self.step_by_step_active = False
                    return "🎉 Congratulations! You've completed the dev setup guide. Your development environment should now be ready!"
            
            elif message_stripped in ("back", "previous"):
                prev_step = self.dev_setup_assistant.previous_step()
                if prev_step:
                    return self.dev_setup_assistant.format_current_step()
                else:
                    return "You're already at the first step."
            
            elif message_stripped in ("status", "progress"):
                progress = self.dev_setup_assistant.get_step_progress()
                return f"""📊 **Setup Progress:** Step {progress['current_step']} of {progress['total_steps']} ({progress['percentage']:.0f}%)

{self.dev_setup_assistant.format_current_step()}"""
        
        elif message_stripped == "help":
            return """🔧 **Dev Setup Assistant Help:**

You can chat naturally with me! For example:
- Say **"step by step"** to start the guided installation walkthrough
- Ask any question about the dev setup (e.g., "What is Colima?")
- Describe errors you're encountering and I'll help troubleshoot

**During step-by-step mode:** `next`, `back`, `status`, `start`"""
        
        # LLM-first: send everything through the LLM for understanding
        return self.dev_setup_assistant.process_with_llm(message, self.conversation_history)
    
    def handle_onboarding_message(self, message: str) -> str:
        """Handle onboarding specific messages."""
        return """📅 **Onboarding Scheduler** (Coming Soon!)

This feature will help you:
- Create onboarding schedules based on class availability
- Coordinate meetings and group sessions
- Generate structured agendas
- Track onboarding progress

For now, I can help with dev setup and general team support. Would you like to start the dev setup guide?"""
    
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