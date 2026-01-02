import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration."""
    
    # App
    APP_NAME: str = "Reception Voice Agent API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:password@localhost/reception_agent"
    )
    
    # Groq API
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_STT_MODEL: str = "whisper-large-v3-turbo"
    GROQ_LLM_MODEL: str = "llama-3.1-8b-instant"
    GROQ_TTS_MODEL: str = "canopylabs/orpheus-v1-english"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
    ]
    
    # Voice
    SAMPLE_RATE: int = 16000
    CHANNELS: int = 1
    VOICE_TIMEOUT: int = 30
    MAX_AUDIO_DURATION: int = 600  # 10 minutes
    
    # LLM
    MAX_RESPONSE_LENGTH: int = 500
    LLM_TEMPERATURE: float = 0.7
    LLM_TOP_P: float = 0.9
    
    # RAG
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 100
    RAG_TOP_K: int = 3
    
    # Cache
    CACHE_TTL_SECONDS: int = 3600
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
