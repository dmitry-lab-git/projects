import traceback
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Проверяем существование файла .env перед передачей в pydantic
ENV_PATH = Path("/home/fujitsu-u745/Projects/secure_folder/eco_service/.env")

class AppSettings(BaseSettings):
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="auroville_eco_service", alias="DB_NAME")
    db_user: str = Field(default="eco_service_app", alias="DB_USER")
    db_password: str = Field(default="", alias="DB_PASSWORD")
    
    db_timezone: str = Field(default="UTC", alias="DB_TIMEZONE")
    db_search_path: str = Field(default="infrastructure,dicts,security,public", alias="DB_SEARCH_PATH")
    
    app_env: str = Field(default="development", alias="APP_ENV")

    model_config = SettingsConfigDict(
        env_file=ENV_PATH if ENV_PATH.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def database_dsn(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

# Гарантированное создание переменной settings с защитой от падений импорта
try:
    settings = AppSettings()
except Exception as e:
    print("\n" + "="*60)
    print(f"CRITICAL CONFIG WARNING: {e}")
    traceback.print_exc()
    print("="*60 + "\n")
    # Создаем дефолтный экземпляр, чтобы приложение запустилось и не ломало импорты
    settings = AppSettings(_env_file=None)