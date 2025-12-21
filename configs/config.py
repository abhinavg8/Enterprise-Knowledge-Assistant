"""
Configuration settings for Enterprise Knowledge Assistant
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = DATA_DIR / "sample_docs"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"

# Embedding model configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Fast and efficient
# Alternative: "sentence-transformers/all-mpnet-base-v2"  # Better quality, slower

# LLM Configuration
# Hugging Face LLM
HF_MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"  # Requires HF token and approval
# Alternative smaller models for testing:
# "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # Very fast, good for testing
# "mistralai/Mistral-7B-Instruct-v0.1"  # Good balance

# OpenAI Configuration (optional)
OPENAI_MODEL = "gpt-3.5-turbo"  # or "gpt-4"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Retrieval configuration
CHUNK_SIZE = 1000  # Characters per chunk
CHUNK_OVERLAP = 200  # Overlap between chunks
TOP_K_RESULTS = 5  # Number of documents to retrieve

# Generation configuration
MAX_NEW_TOKENS = 512
TEMPERATURE = 0.7
TOP_P = 0.95

# Vector store configuration
VECTOR_STORE_TYPE = "faiss"  # Using FAISS as specified

# Document processing
SUPPORTED_EXTENSIONS = [".txt", ".pdf", ".docx", ".md", ".html"]

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "logs" / "app.log"

# Create necessary directories
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "logs").mkdir(exist_ok=True)
