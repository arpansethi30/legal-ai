# backend/src/config/settings.py
import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define environment configurations
class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Legal AI"
    APP_VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Model settings
    GEMINI_FLASH_MODEL: str = "gemini-1.5-flash"
    GEMINI_PRO_MODEL: str = "gemini-1.5-pro"
    
    # Environment
    ENV: str = os.getenv("ENV", "development")
    
    # Storage
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    
    # Ensure required directories exist
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """
    Get settings singleton using LRU cache for performance
    """
    # Create upload directory if it doesn't exist
    settings = Settings()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    return settings 