import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API keys for sponsor tools
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    STYTCH_PROJECT_ID: str = os.getenv("STYTCH_PROJECT_ID", "")
    STYTCH_SECRET: str = os.getenv("STYTCH_SECRET", "")
    APIFY_API_TOKEN: str = os.getenv("APIFY_API_TOKEN", "")
    LANGTRACE_API_KEY: str = os.getenv("LANGTRACE_API_KEY", "")
    
    # App settings
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()