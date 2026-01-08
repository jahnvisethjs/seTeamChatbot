#!/usr/bin/env python3
"""
Setup script for SE Team Mega Chatbot
"""

import os
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from example if it doesn't exist."""
    env_file = Path(".env")
    example_file = Path("env_example.txt")
    
    if not env_file.exists() and example_file.exists():
        shutil.copy(example_file, env_file)
        print("✅ Created .env file from example")
        print("⚠️  Please edit .env file and add your OpenAI API key")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("❌ Could not create .env file - env_example.txt not found")

def create_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        "data",
        "data/knowledge_base",
        "config",
        "chatbot"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        print("✅ Streamlit is installed")
    except ImportError:
        print("❌ Streamlit not found. Run: pip install -r requirements.txt")
    
    try:
        import langchain
        print("✅ LangChain is installed")
    except ImportError:
        print("❌ LangChain not found. Run: pip install -r requirements.txt")

def main():
    """Main setup function."""
    print("🚀 Setting up SE Team Mega Chatbot...")
    print()
    
    # Create directories
    create_directories()
    print()
    
    # Create .env file
    create_env_file()
    print()
    
    # Check dependencies
    check_dependencies()
    print()
    
    print("🎉 Setup complete!")
    print()
    print("Next steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: streamlit run app.py")
    print("3. Open your browser to the provided URL")
    print()
    print("For help, see README.md")

if __name__ == "__main__":
    main() 