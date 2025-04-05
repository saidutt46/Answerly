"""
Configuration settings for the QA Model Application
"""
import os
from typing import List, Dict, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings.
    
    These settings can be overridden with environment variables.
    """
    # Server settings
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )
    
    # File upload settings
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".txt", ".pdf"], 
        env="ALLOWED_EXTENSIONS"
    )
    
    # Model settings
    DEFAULT_MODEL: str = Field(
        default="distilbert-base-uncased-distilled-squad",
        env="DEFAULT_MODEL"
    )
    
    MODEL_CACHE_DIR: str = Field(default="model_cache", env="MODEL_CACHE_DIR")
    
    MODELS: Dict[str, str] = {
        "DistilBERT (Fast)": "distilbert-base-uncased-distilled-squad",
        "RoBERTa (Balanced)": "deepset/roberta-base-squad2",
        "BERT Large (Accurate)": "bert-large-uncased-whole-word-masking-finetuned-squad",
        "ELECTRA Small (Lightweight)": "google/electra-small-discriminator"
    }
    
    # Document processing settings
    MAX_SEQ_LENGTH: int = Field(default=512, env="MAX_SEQ_LENGTH")
    CHUNK_SIZE: int = Field(default=475, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=100, env="CHUNK_OVERLAP")
    
    # Performance settings
    BATCH_SIZE: int = Field(default=1, env="BATCH_SIZE")
    NUM_WORKERS: int = Field(default=1, env="NUM_WORKERS")
    USE_GPU: bool = Field(default=True, env="USE_GPU")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)