"""Application configuration management."""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "CRAG System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "production", "staging"] = "development"

    OPENAI_API_KEY: str
    BRAVE_API_KEY: str

    MODEL_NAME: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    TEMPERATURE: float = 0.0

    VECTORSTORE_PATH: str = "vectorstore"
    DATA_PATH: str = "data"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 10

    GRADE_THRESHOLD: float = 0.7
    MIN_RELEVANT_CHUNKS: int = 2

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    API_RATE_LIMIT: int = 100

    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
