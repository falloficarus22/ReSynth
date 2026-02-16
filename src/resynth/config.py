"""
Configuration settings for ReSynth
"""

import os
from dotenv import load_dotenv

# Try to load .env, but don't fail if it doesn't exist (for Colab/cloud environments)
load_dotenv(override=False)

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Model Settings
    HUGGINGFACE_MODEL_NAME = os.getenv("HUGGINGFACE_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Vector Database - Use /content for Colab, ./ for local
    if os.path.exists("/content"):
        # Google Colab environment
        CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "/content/chroma_db")
        PAPER_DOWNLOAD_DIR = os.getenv("PAPER_DOWNLOAD_DIR", "/content/papers")
    else:
        # Local/other environments
        CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
        PAPER_DOWNLOAD_DIR = os.getenv("PAPER_DOWNLOAD_DIR", "./papers")
    
    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "research_papers")
    
    # Paper Fetching
    MAX_PAPERS_PER_QUERY = int(os.getenv("MAX_PAPERS_PER_QUERY", "10"))
    
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
    def setup_for_colab(cls, openai_api_key=None):
        """Helper function to setup ReSynth for Google Colab"""
        if os.path.exists("/content"):
            print("Setting up ReSynth for Google Colab...")
            
            # Set environment variables for Colab
            os.environ["CHROMA_PERSIST_DIRECTORY"] = "/content/chroma_db"
            os.environ["PAPER_DOWNLOAD_DIR"] = "/content/papers"
            
            if openai_api_key:
                os.environ["OPENAI_API_KEY"] = openai_api_key
                print("OpenAI API key set")
            
            print("Colab configuration complete!")
            print(f"Database will be stored at: /content/chroma_db")
            print(f"Papers will be downloaded to: /content/papers")
        else:
            print("Not running in Google Colab")
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        issues = []
        
        if not cls.OPENAI_API_KEY:
            issues.append("OpenAI API key not set (optional but recommended)")
        
        try:
            os.makedirs(cls.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
            os.makedirs(cls.PAPER_DOWNLOAD_DIR, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create directories: {e}")
        
        return issues
