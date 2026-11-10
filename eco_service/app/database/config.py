from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Absolute path to the .env file within the WSL environment
ENV_PATH = Path("/home/fujitsu-u745/Projects/secure_folder/eco_service/.env")

class AppSettings(BaseSettings):
    # Unified database connection string (as in your working configuration)
    database_url: str = Field(..., alias="DATABASE_URL")
    
    # Context Session Settings
    db_timezone: str = Field(default="UTC", alias="DB_TIMEZONE")
    db_search_path: str = Field(default="infrastructure,dicts,security,public", alias="DB_SEARCH_PATH")
    
    # System Runtime Context
    app_env: str = Field(default="development", alias="APP_ENV")

    model_config = SettingsConfigDict(
        env_file=ENV_PATH if ENV_PATH.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Configuration initialization
settings = AppSettings()

