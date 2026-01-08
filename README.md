# SE Team Mega Chatbot

A comprehensive chatbot solution for the SE team with multiple integrated functionalities:

## Features

### 1. Dev Setup Assistant (Primary Focus)
- Step-by-step guidance through development environment setup
- Error detection and resolution using FAQ knowledge base
- Interactive command execution guidance
- Progress tracking and validation

### 2. Onboarding Scheduler (Future)
- Automated schedule creation based on class schedules
- Meeting coordination and availability matching
- Template reuse from previous onboarding sessions

### 3. RAG-based Support System
- Intelligent document retrieval
- Context-aware responses
- Access to Confluence documents, templates, and guides

## Project Structure

```
seTeamChatbot/
├── app.py                 # Main Streamlit application
├── chatbot/
│   ├── __init__.py
│   ├── core.py           # Core chatbot logic
│   ├── dev_setup.py      # Dev setup specific functionality
│   ├── rag_engine.py     # RAG implementation
│   └── utils.py          # Utility functions
├── data/
│   ├── dev_setup_guide.md # Dev setup documentation
│   ├── faq.md            # Common errors and solutions
│   └── knowledge_base/   # Additional documents
├── config/
│   └── settings.py       # Configuration settings
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd seTeamChatbot
   python setup.py
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   - Copy `env_example.txt` to `.env`
   - Add your ASU AI API token to the `.env` file:
   ```
   ASU_AI_API_TOKEN=your_asu_ai_api_token_here
   ```
   - Get your API token from: https://platform.aiml.asu.edu

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

5. **Access the Application**
   - Open your browser to the URL shown in the terminal (usually http://localhost:8501)
   - The chatbot will be ready to use!

## Usage

1. **Dev Setup Mode**: Select "Dev Setup Assistant" to get step-by-step guidance
2. **General Support**: Use the main chat for general questions and document retrieval
3. **Error Resolution**: The bot will automatically detect errors and provide solutions

## Development

- The chatbot uses RAG (Retrieval-Augmented Generation) for intelligent responses
- Powered by ASU AI Platform (CreateAI) with GPT-5 model
- Uses ASU-hosted embeddings for fast vector generation
- Modular design allows easy addition of new features
- Streamlit provides a clean, interactive interface
- Knowledge base can be easily updated with new documents

## Customization

### Dev Setup Guide
To customize the dev setup guide for your team:
1. Edit `data/dev_setup_guide.md` with your specific setup steps
2. Follow the numbered format: `1. **Step Title**`
3. Include commands in code blocks: ```bash
4. Add verification checks: `- [ ] Check item`

### Knowledge Base
To add team-specific documentation:
1. Add markdown files to `data/knowledge_base/`
2. Include team guides, processes, and FAQs
3. The RAG system will automatically index new documents
4. Restart the application to load new content

### Error Resolution
To add custom error solutions:
1. Edit `data/faq.md` with common errors and solutions
2. Use the format: `**Error: [error description]**`
3. Follow with: `- Solution: [solution steps]`

## Deployment

The application can be deployed on Streamlit Community Cloud for free sharing and collaboration. 