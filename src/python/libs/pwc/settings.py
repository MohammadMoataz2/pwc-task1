import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # App
    app_name: str = "pwc.contract.analysis"
    app_version: str = "1.0.0"
    debug: bool = False

    # API
    api_v1_prefix: str = "/api/v1"
    api_base_url: str = Field(default="http://api:8000")  # URL for worker callbacks
    secret_key: str = Field(default="your-secret-key-change-this")
    access_token_expire_minutes: int = 30

    # Database
    mongodb_url: str = Field(default="mongodb://localhost:27017")
    mongodb_database: str = Field(default="pwc_contracts")

    # Redis/Celery
    redis_url: str = Field(default="redis://localhost:6379/0")
    celery_broker_url: str = Field(default="redis://localhost:6379/0")
    celery_result_backend: str = Field(default="redis://localhost:6379/0")

    # Storage Factory
    storage_type: str = Field(default="local")  # local, s3 (future)
    local_storage_path: str = Field(default="./storage")

    # AI Factory
    ai_provider: str = Field(default="openai")  # openai, huggingface (future)
    openai_api_key: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4")

    # CORS
    backend_cors_origins: List[str] = Field(default_factory=list)

    # Authentication
    auth_username: str = Field(default="admin")
    auth_password: str = Field(default="admin123")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()