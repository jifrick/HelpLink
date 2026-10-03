import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "HelpLink"
    ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "helplink_dev_secret_key_change_in_prod_2026_987654321"
    DATABASE_URL: str = "sqlite:///./helplink.db"
    
    ADMIN_INITIAL_EMAIL: str = "admin@helplink.org"
    ADMIN_INITIAL_PASSWORD: str = "AdminSecurePassword123!"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
