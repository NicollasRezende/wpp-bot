from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, validator
from typing import Optional, Dict, Any, List
import os
from pathlib import Path


class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "WhatsApp API Template"
    DEBUG: bool = False
    SECRET_KEY: str
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database settings
    DATABASE_URL: PostgresDsn
    
    # WhatsApp API settings
    WHATSAPP_TOKEN: str
    VERIFY_TOKEN: str
    BASE_URL: str
    PAGE_ID: str
    
    # Business hours
    BUSINESS_HOURS_START: int = 8  # 8 AM
    BUSINESS_HOURS_END: int = 18   # 6 PM
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    MEDIA_PATH: str = str(BASE_DIR / "media")
    LOG_PATH: str = str(BASE_DIR / "logs")
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @validator("MEDIA_PATH", "LOG_PATH")
    def create_directories(cls, v):
        os.makedirs(v, exist_ok=True)
        return v


settings = Settings()