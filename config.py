import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Temporal configuration
TEMPORAL_HOST = os.getenv("TEMPORAL_HOST", "localhost:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "telegram-agent-queue")

# Optional TLS configuration
TEMPORAL_TLS_CERT = os.getenv("TEMPORAL_TLS_CERT")
TEMPORAL_TLS_KEY = os.getenv("TEMPORAL_TLS_KEY")
TEMPORAL_TLS_CA = os.getenv("TEMPORAL_TLS_CA")

# TLS configuration if certificates are provided
TLS_CONFIG = None
if all([TEMPORAL_TLS_CERT, TEMPORAL_TLS_KEY, TEMPORAL_TLS_CA]):
    TLS_CONFIG = {
        "client_cert": TEMPORAL_TLS_CERT,
        "client_private_key": TEMPORAL_TLS_KEY,
        "server_root_ca_cert": TEMPORAL_TLS_CA,
    }

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "ai_agent_db")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "telegram_requests")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Telegram configuration
AUTHORIZED_USER_ID = int(os.getenv("AUTHORIZED_USER_ID", "265278326"))

# Streamlit configuration
STREAMLIT_PASSWORD = os.getenv("STREAMLIT_PASSWORD", "admin123")
STREAMLIT_HOST = os.getenv("STREAMLIT_HOST", "0.0.0.0")
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

# Sentiment Analysis (optional)
SENTIMENT_API_ENABLED = os.getenv("SENTIMENT_API_ENABLED", "false").lower() == "true"
SENTIMENT_API_URL = os.getenv("SENTIMENT_API_URL")

# Retry configuration
LLM_RETRY_ATTEMPTS = int(os.getenv("LLM_RETRY_ATTEMPTS", "3"))
LLM_RETRY_BACKOFF = int(os.getenv("LLM_RETRY_BACKOFF", "10"))

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO") 