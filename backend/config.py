from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "sqlite:///./ckempire.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Application
    APP_NAME: str = "Advanced CK Empire Builder"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    
    # AI Settings
    AI_MODEL: str = "gpt-4"
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.7
    
    # Ethics Module
    ETHICS_ENABLED: bool = True
    BIAS_DETECTION_THRESHOLD: float = 0.8
    
    # Video Generation
    VIDEO_OUTPUT_DIR: str = "generated_videos"
    VIDEO_MAX_DURATION: int = 300  # 5 minutes
    
    # NFT Settings
    NFT_CONTRACT_ADDRESS: Optional[str] = None
    WEB3_PROVIDER_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Validate required settings
def validate_settings():
    """Validate required settings"""
    if not settings.OPENAI_API_KEY:
        print("⚠️  Warning: OPENAI_API_KEY not set")
    
    if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-change-in-production":
        print("⚠️  Warning: SECRET_KEY should be changed in production")

# Run validation
validate_settings() 