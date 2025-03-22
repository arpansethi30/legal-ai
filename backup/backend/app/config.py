import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # App settings
    APP_NAME = "Legal AI"
    APP_VERSION = "0.1.0"
    API_PREFIX = "/api"
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Model settings
    GEMINI_FLASH_MODEL = "gemini-1.5-flash"
    GEMINI_PRO_MODEL = "gemini-1.5-pro"
    
    # Storage
    UPLOAD_DIR = "uploads"
    
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize settings
settings = Settings()