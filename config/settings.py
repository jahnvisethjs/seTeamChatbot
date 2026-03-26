import os
from dotenv import load_dotenv

# Load environment variables from .env (for local development)
load_dotenv()

# ASU AI Platform Configuration
# Support both Streamlit Cloud secrets and local .env file.
# On Streamlit Cloud, secrets are in st.secrets (NOT env vars),
# so we inject them into os.environ for all downstream code.
try:
    import streamlit as st
    if "ASU_AI_API_TOKEN" in st.secrets:
        os.environ["ASU_AI_API_TOKEN"] = st.secrets["ASU_AI_API_TOKEN"]
except Exception:
    pass  # Not running in Streamlit, or secrets not configured

ASU_AI_API_TOKEN = os.getenv("ASU_AI_API_TOKEN")
ASU_AI_BASE_URL = "https://api-main.aiml.asu.edu"
ASU_AI_MODEL = "gpt-4o"
ASU_AI_EMBEDDINGS_MODEL = "text-embedding-ada-002"
ASU_AI_EMBEDDINGS_URL = "https://api-main.aiml.asu.edu/embeddings"
ASU_AI_QUERY_URL = "https://api-main.aiml.asu.edu/query"
ASU_AI_QUERY_V2_URL = "https://api-main.aiml.asu.edu/queryV2"

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 3

# Application Settings
APP_TITLE = "SE Team Chatbot"
APP_DESCRIPTION = "Your comprehensive assistant for dev setup, onboarding, and team support"

# File Paths
DATA_DIR = "data"
KNOWLEDGE_BASE_DIR = os.path.join(DATA_DIR, "knowledge_base")
DEV_SETUP_GUIDE = os.path.join(DATA_DIR, "dev_setup_guide.md")
FAQ_FILE = os.path.join(DATA_DIR, "faq.md")

# Chatbot Settings
MAX_HISTORY_LENGTH = 10
TEMPERATURE = 0.7
MAX_TOKENS = 1000 