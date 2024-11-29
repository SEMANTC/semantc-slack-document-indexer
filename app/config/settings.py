# app/config/settings.py

from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """
    APPLICATION SETTINGS. THESE ARE LOADED FROM ENVIRONMENT VARIABLES
    USES PYDANTIC FOR VALIDATION AND TYPE CHECKING
    """
    # google cloud settings
    PROJECT_ID: str
    REGION: str = "us-central1"
    
    # google drive settings
    DRIVE_FOLDER_ID: str
    
    # vector db settings (pinecone)
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX_NAME: str
    
    # openai settings
    OPENAI_API_KEY: str

    # claude ai settings
    ANTHROPIC_API_KEY: str
    
    # processing settings
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100
    MAX_CHUNKS_PER_DOC: int = 100

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    CREATES AND CACHES SETTINGS INSTANCE
    RETURNS THE SAME INSTANCE FOR SUBSEQUENT CALLS
    """
    return Settings()