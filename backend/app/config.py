"""Configuration for AI voice receptionist."""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Application settings."""
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
    
    # LLM Config
    LLM_MODEL: str = os.getenv("LLM_MODEL", "mixtral-8x7b-32768")  # Groq model
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 500
    
    # Voice Config
    SAMPLE_RATE: int = 16000
    CHANNELS: int = 1
    VOICE_TIMEOUT: int = 30
    
    # TTS Provider
    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "groq")  # or "deepgram"
    
    # Storage
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
