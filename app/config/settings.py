# app/config/settings.py

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Google Cloud Settings
    PROJECT_ID: str
    REGION: str = "us-central1"
    GOOGLE_APPLICATION_CREDENTIALS: str

    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    OAUTH_REDIRECT_URI: str

    # AI Model Settings
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str

    # Vector DB Settings (Pinecone)
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX_NAME: str

    # Application Settings
    APP_PORT: int = 8080
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()