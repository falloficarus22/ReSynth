"""
Configuration settings for ReSynth
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Model Settings
    HUGGINGFACE_MODEL_NAME = os.getenv("HUGGINGFACE_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "research_papers")
    
    # Paper Fetching
    MAX_PAPERS_PER_QUERY = int(os.getenv("MAX_PAPERS_PER_QUERY", "10"))
    PAPER_DOWNLOAD_DIR = os.getenv("PAPER_DOWNLOAD_DIR", "./papers")
    
    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    # Chunking Settings
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Retrieval Settings
    TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    
    @classmethod
    def validate(cls):
        """Validate configuration settings"""
        if not cls.OPENAI_API_KEY:
            print("Warning: OPENAI_API_KEY not set. Some features may not work.")
        
        # Create necessary directories
        os.makedirs(cls.PAPER_DOWNLOAD_DIR, exist_ok=True)
        os.makedirs(cls.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
