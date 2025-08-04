"""
Central Configuration Management for CK Empire Builder
Handles all configuration settings, environment variables, and constants
"""

import os
from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import validator, Field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Environment(str, Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class DatabaseType(str, Enum):
    """Database types"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"

class CloudProvider(str, Enum):
    """Cloud providers"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    NONE = "none"

class Settings(BaseSettings):
    """Central application settings"""
    
    # Environment
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Application
    APP_NAME: str = "CK Empire Builder"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=1, description="Number of workers")
    
    # Database
    DATABASE_TYPE: DatabaseType = DatabaseType.SQLITE
    DATABASE_URL: str = Field(default="sqlite:///./ckempire.db", description="Database URL")
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Database max overflow")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis URL")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    
    # Security
    SECRET_KEY: str = Field(default="", description="Secret key for JWT")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Token expiration")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"],
        description="Allowed hosts"
    )
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, description="Rate limit per minute")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="Rate limit per hour")
    
    # File Upload
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, description="Max file size (10MB)")
    UPLOAD_DIR: str = Field(default="uploads", description="Upload directory")
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"],
        description="Allowed file types"
    )
    
    # AI Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    AI_MODEL: str = Field(default="gpt-4", description="Default AI model")
    AI_MAX_TOKENS: int = Field(default=2000, description="Max tokens for AI")
    AI_TEMPERATURE: float = Field(default=0.7, description="AI temperature")
    AI_TIMEOUT: int = Field(default=30, description="AI request timeout")
    
    # Ethics Module
    ETHICS_ENABLED: bool = Field(default=True, description="Enable ethics monitoring")
    BIAS_DETECTION_THRESHOLD: float = Field(default=0.8, description="Bias detection threshold")
    ETHICS_CHECK_INTERVAL: int = Field(default=300, description="Ethics check interval (seconds)")
    
    # Video Generation
    VIDEO_OUTPUT_DIR: str = Field(default="generated_videos", description="Video output directory")
    VIDEO_MAX_DURATION: int = Field(default=300, description="Max video duration (seconds)")
    VIDEO_QUALITY: str = Field(default="1080p", description="Video quality")
    
    # NFT Configuration
    NFT_CONTRACT_ADDRESS: Optional[str] = Field(default=None, description="NFT contract address")
    WEB3_PROVIDER_URL: Optional[str] = Field(default=None, description="Web3 provider URL")
    ETHEREUM_RPC_URL: Optional[str] = Field(default=None, description="Ethereum RPC URL")
    ETHEREUM_PRIVATE_KEY: Optional[str] = Field(default=None, description="Ethereum private key")
    
    # Stripe Payments
    STRIPE_SECRET_KEY: Optional[str] = Field(default=None, description="Stripe secret key")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = Field(default=None, description="Stripe publishable key")
    STRIPE_WEBHOOK_SECRET: Optional[str] = Field(default=None, description="Stripe webhook secret")
    
    # OAuth2 Settings
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, description="Google OAuth client ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None, description="Google OAuth client secret")
    GITHUB_CLIENT_ID: Optional[str] = Field(default=None, description="GitHub OAuth client ID")
    GITHUB_CLIENT_SECRET: Optional[str] = Field(default=None, description="GitHub OAuth client secret")
    MICROSOFT_CLIENT_ID: Optional[str] = Field(default=None, description="Microsoft OAuth client ID")
    MICROSOFT_CLIENT_SECRET: Optional[str] = Field(default=None, description="Microsoft OAuth client secret")
    
    # Cloud Configuration
    CLOUD_PROVIDER: CloudProvider = CloudProvider.NONE
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="AWS access key ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="AWS secret access key")
    AWS_REGION: str = Field(default="us-east-1", description="AWS region")
    GCP_PROJECT_ID: Optional[str] = Field(default=None, description="GCP project ID")
    GCP_CREDENTIALS_FILE: Optional[str] = Field(default=None, description="GCP credentials file")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, description="Sentry DSN")
    PROMETHEUS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics")
    LOG_LEVEL: str = Field(default="INFO", description="Log level")
    
    # Encryption
    ENCRYPTION_KEY: Optional[str] = Field(default=None, description="Encryption key")
    
    # Backup
    AUTO_BACKUP_ENABLED: bool = Field(default=True, description="Enable auto backup")
    BACKUP_INTERVAL_HOURS: int = Field(default=24, description="Backup interval in hours")
    BACKUP_RETENTION_DAYS: int = Field(default=30, description="Backup retention in days")
    
    # Performance
    CACHE_TTL: int = Field(default=3600, description="Cache TTL in seconds")
    SESSION_TIMEOUT: int = Field(default=1800, description="Session timeout in seconds")
    
    # Video Production Tools
    DAVINCI_PATH: Optional[str] = Field(default=None, description="DaVinci Resolve path")
    CAPCUT_PATH: Optional[str] = Field(default=None, description="CapCut path")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = "CK_"
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v):
        """Validate secret key"""
        if not v or v == "your-secret-key-change-in-production":
            if os.getenv("ENVIRONMENT") == "production":
                raise ValueError("SECRET_KEY must be set in production")
            else:
                # Generate a random key for development
                import secrets
                v = secrets.token_urlsafe(32)
                logger.warning("Generated random SECRET_KEY for development")
        return v
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v, values):
        """Validate database URL"""
        if not v:
            if values.get("DATABASE_TYPE") == DatabaseType.SQLITE:
                v = "sqlite:///./ckempire.db"
            elif values.get("DATABASE_TYPE") == DatabaseType.POSTGRESQL:
                v = "postgresql://user:password@localhost/ckempire"
            elif values.get("DATABASE_TYPE") == DatabaseType.MYSQL:
                v = "mysql://user:password@localhost/ckempire"
        return v
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def validate_allowed_origins(cls, v):
        """Validate allowed origins"""
        if not v:
            v = ["http://localhost:3000", "http://localhost:8080"]
        return v
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    def is_testing(self) -> bool:
        """Check if running in testing"""
        return self.ENVIRONMENT == Environment.TESTING
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": self.DATABASE_POOL_SIZE,
            "max_overflow": self.DATABASE_MAX_OVERFLOW,
            "echo": self.DEBUG
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        return {
            "url": self.REDIS_URL,
            "db": self.REDIS_DB,
            "password": self.REDIS_PASSWORD
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            "secret_key": self.SECRET_KEY,
            "algorithm": self.ALGORITHM,
            "access_token_expire_minutes": self.ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_token_expire_days": self.REFRESH_TOKEN_EXPIRE_DAYS
        }
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI configuration"""
        return {
            "api_key": self.OPENAI_API_KEY,
            "model": self.AI_MODEL,
            "max_tokens": self.AI_MAX_TOKENS,
            "temperature": self.AI_TEMPERATURE,
            "timeout": self.AI_TIMEOUT
        }
    
    def get_cloud_config(self) -> Dict[str, Any]:
        """Get cloud configuration"""
        return {
            "provider": self.CLOUD_PROVIDER,
            "aws": {
                "access_key_id": self.AWS_ACCESS_KEY_ID,
                "secret_access_key": self.AWS_SECRET_ACCESS_KEY,
                "region": self.AWS_REGION
            },
            "gcp": {
                "project_id": self.GCP_PROJECT_ID,
                "credentials_file": self.GCP_CREDENTIALS_FILE
            }
        }
    
    def validate_required_settings(self) -> Dict[str, List[str]]:
        """Validate required settings for current environment"""
        errors = []
        warnings = []
        
        # Required for all environments
        if not self.SECRET_KEY:
            errors.append("SECRET_KEY is required")
        
        # Production requirements
        if self.is_production():
            if not self.OPENAI_API_KEY:
                warnings.append("OPENAI_API_KEY recommended for production")
            if not self.STRIPE_SECRET_KEY:
                warnings.append("STRIPE_SECRET_KEY recommended for production")
            if self.CLOUD_PROVIDER == CloudProvider.NONE:
                warnings.append("Cloud provider recommended for production")
        
        # Development warnings
        if self.is_development():
            if self.SECRET_KEY == "your-secret-key-change-in-production":
                warnings.append("SECRET_KEY should be changed in production")
        
        return {"errors": errors, "warnings": warnings}

# Create settings instance
settings = Settings()

# Validate settings on import
def validate_and_log_settings():
    """Validate settings and log any issues"""
    validation = settings.validate_required_settings()
    
    if validation["errors"]:
        logger.error("Configuration errors found:")
        for error in validation["errors"]:
            logger.error(f"  - {error}")
        raise ValueError("Configuration validation failed")
    
    if validation["warnings"]:
        logger.warning("Configuration warnings:")
        for warning in validation["warnings"]:
            logger.warning(f"  - {warning}")

# Run validation
validate_and_log_settings()

# Constants
class Constants:
    """Application constants"""
    
    # API Versions
    API_V1 = "v1"
    
    # HTTP Status Codes
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_429_TOO_MANY_REQUESTS = 429
    HTTP_500_INTERNAL_SERVER_ERROR = 500
    HTTP_503_SERVICE_UNAVAILABLE = 503
    
    # Rate Limiting
    DEFAULT_RATE_LIMIT = "100/minute"
    AUTH_RATE_LIMIT = "10/minute"
    METRICS_RATE_LIMIT = "30/minute"
    
    # Cache Keys
    CACHE_KEY_PREFIX = "ckempire:"
    USER_CACHE_TTL = 3600
    PROJECT_CACHE_TTL = 1800
    METRICS_CACHE_TTL = 300
    
    # File Upload
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]
    ALLOWED_DOCUMENT_TYPES = ["application/pdf", "application/msword", 
                              "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    # AI Models
    DEFAULT_AI_MODEL = "gpt-4"
    FALLBACK_AI_MODEL = "gpt-3.5-turbo"
    
    # Video Settings
    DEFAULT_VIDEO_QUALITY = "1080p"
    DEFAULT_VIDEO_FPS = 30
    MAX_VIDEO_DURATION = 300  # 5 minutes
    
    # NFT Settings
    DEFAULT_NFT_STANDARD = "ERC-721"
    DEFAULT_NFT_METADATA_VERSION = "1.0"
    
    # Security
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128
    SESSION_TIMEOUT_SECONDS = 1800  # 30 minutes
    
    # Monitoring
    HEALTH_CHECK_INTERVAL = 30  # seconds
    METRICS_COLLECTION_INTERVAL = 60  # seconds
    
    # Database
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Content Types
    CONTENT_TYPE_ARTICLE = "article"
    CONTENT_TYPE_VIDEO = "video"
    CONTENT_TYPE_SOCIAL = "social"
    CONTENT_TYPE_PODCAST = "podcast"
    CONTENT_TYPE_NFT = "nft"
    
    # Project Status
    PROJECT_STATUS_DRAFT = "draft"
    PROJECT_STATUS_ACTIVE = "active"
    PROJECT_STATUS_COMPLETED = "completed"
    PROJECT_STATUS_CANCELLED = "cancelled"
    
    # Revenue Sources
    REVENUE_SOURCE_ADS = "ads"
    REVENUE_SOURCE_SUBSCRIPTION = "subscription"
    REVENUE_SOURCE_PRODUCT = "product"
    REVENUE_SOURCE_SERVICE = "service"
    REVENUE_SOURCE_AFFILIATE = "affiliate"
    
    # Subscription Tiers
    SUBSCRIPTION_TIER_FREEMIUM = "freemium"
    SUBSCRIPTION_TIER_PREMIUM = "premium"
    SUBSCRIPTION_TIER_ENTERPRISE = "enterprise"
    
    # Ethics Status
    ETHICS_STATUS_APPROVED = "approved"
    ETHICS_STATUS_FLAGGED = "flagged"
    ETHICS_STATUS_REJECTED = "rejected"
    ETHICS_STATUS_NEEDS_REVIEW = "needs_review"

# Create constants instance
constants = Constants() 