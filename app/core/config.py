import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List

load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Ecofy Backend API"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ecofy.db")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # External APIs
    WEATHER_API_KEY: Optional[str] = os.getenv("WEATHER_API_KEY")
    SATELLITE_API_KEY: Optional[str] = os.getenv("SATELLITE_API_KEY")
    
    # ISDA Africa API credentials
    ISDA_USERNAME: str = os.getenv("ISDA_USERNAME", "lugata619@gmail.com")
    ISDA_PASSWORD: str = os.getenv("ISDA_PASSWORD", "gnt6192002")
    
    class Config:
        case_sensitive = True


settings = Settings() 