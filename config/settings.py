import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ASU AI Platform Configuration
ASU_AI_API_TOKEN = os.getenv("ASU_AI_API_TOKEN")
ASU_AI_BASE_URL = "https://api-main.aiml.asu.edu"
ASU_AI_MODEL = "gpt-5"
ASU_AI_EMBEDDINGS_MODEL = "text-embedding-ada-002"
ASU_AI_EMBEDDINGS_URL = "https://api-main.aiml.asu.edu/embeddings"
ASU_AI_QUERY_URL = "https://api-main.aiml.asu.edu/query"

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 3

# Application Settings
APP_TITLE = "SE Team Mega Chatbot"
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