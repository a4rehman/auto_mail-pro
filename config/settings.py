import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Apify
    APIFY_API_TOKEN: str = ""
    APIFY_ACTOR_ID: str = ""
    
    # AI
    OPENAI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4o-mini"
    AI_MAX_RETRIES: int = 3
    AI_TEMPERATURE: float = 0.7
    
    # SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SENDER_NAME: str = "100Solutionz"
    SENDER_EMAIL: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///data/leads.db"
    
    # App
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    DRY_RUN: bool = True
    
    # Pipeline
    MAX_CONCURRENT_WEBSITES: int = 5
    MAX_PAGES_PER_WEBSITE: int = 10
    REQUEST_TIMEOUT: int = 30
    MAX_DISCOVERY_RESULTS: int = 100
    
    # Compliance
    BUSINESS_NAME: str = "100Solutionz"
    BUSINESS_ADDRESS: str = ""
    UNSUBSCRIBE_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
