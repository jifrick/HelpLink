import os
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "HelpLink"
    ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "helplink_dev_secret_key_change_in_prod_2026_987654321"
    DATABASE_URL: str = "sqlite:///./helplink.db"
    
    ADMIN_INITIAL_EMAIL: str = "admin@helplink.org"
    ADMIN_INITIAL_PASSWORD: str = "AdminDevPassword123!"

    # Development Auth Bypass (Development Mode Only)
    AUTH_BYPASS_ENABLED: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Hardening for Production environments
if settings.ENV == "production":
    if settings.SECRET_KEY == "helplink_dev_secret_key_change_in_prod_2026_987654321":
        raise ValueError("CRITICAL: Production environment detected, but default SECRET_KEY is in use. Set a secure SECRET_KEY in environment variables.")
    if settings.AUTH_BYPASS_ENABLED:
        raise ValueError("CRITICAL: Production environment detected, but AUTH_BYPASS_ENABLED is set to True. Authentication bypass MUST NOT be enabled in production environments.")

