from pydantic_settings import BaseSettings
from typing import Optional, List
import os

# Explicitly define path to .env file in backend directory
# Current file is in backend/app/core/, so we need to go up 3 levels to backend/
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BACKEND_DIR, ".env")

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "JWHD IP Automation"
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: str = ""
    BACKEND_CORS_ORIGINS: List[str] = []

    # Database
    MONGODB_URL: str
    DATABASE_NAME: str = "jwhd_ip_automation"
    
    # Redis Configuration (supports both local and Upstash Redis with SSL)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Google Cloud Storage
    GOOGLE_APPLICATION_CREDENTIALS_JSON: Optional[str] = None
    GCP_BUCKET_NAME: str = "jwhd-ip-automation"
    GCP_STORAGE_BUCKET: Optional[str] = None

    # GCP Service Account Details
    GCP_TYPE: Optional[str] = None
    GCP_PROJECT_ID: Optional[str] = None
    GCP_PRIVATE_KEY_ID: Optional[str] = None
    GCP_PRIVATE_KEY: Optional[str] = None
    GCP_CLIENT_EMAIL: Optional[str] = None
    GCP_CLIENT_ID: Optional[str] = None
    GCP_AUTH_URI: Optional[str] = None
    GCP_TOKEN_URI: Optional[str] = None
    GCP_AUTH_PROVIDER_X509_CERT_URL: Optional[str] = None
    GCP_CLIENT_X509_CERT_URL: Optional[str] = None
    GCP_UNIVERSE_DOMAIN: Optional[str] = None
    
    # Gemini LLM
    GOOGLE_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-pro"
    GEMINI_TEMPERATURE: float = 0.0
    GEMINI_MAX_OUTPUT_TOKENS: int = 65536
    GEMINI_TIMEOUT_SECONDS: int = 900
    GEMINI_MAX_RETRIES: int = 3

    # Extraction Configuration
    CHUNK_SIZE_PAGES: int = 5  # Aligned with Technical Guide
    LARGE_FILE_THRESHOLD_MB: float = 5.0  # Aligned with Technical Guide
    LARGE_FILE_PAGE_THRESHOLD: int = 50
    MAX_CONCURRENT_EXTRACTIONS: int = 5  # Optimal for stability/rate-limits

    # Celery
    @property
    def CELERY_BROKER_URL(self) -> str:
        return self.REDIS_URL
    
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.REDIS_URL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Build CORS origins from FRONTEND_URL and optional CORS_ORIGINS
        if not self.BACKEND_CORS_ORIGINS:
            origins = [self.FRONTEND_URL]
            if self.CORS_ORIGINS:
                origins.extend(
                    o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()
                )
            self.BACKEND_CORS_ORIGINS = list(dict.fromkeys(origins))

    class Config:
        env_file = ENV_PATH
        case_sensitive = True
        extra = "ignore"

settings = Settings()