import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Динамическое определение корня проектов (/home/fujitsu-u745/Projects)
PROJECTS_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_PATH = PROJECTS_ROOT / "secure_folder" / "data_ingress" / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    raise FileNotFoundError(f"Файл конфигурации .env не найден: {ENV_PATH}")

# Базовые пути (Windows-контур через /mnt/c)
INGRESS_ROOT = Path("/mnt/c/Personal/Projects/Ingress")
ARCHIVE_STORAGE = Path("/mnt/c/Personal/Projects/Archive_Buffer")

# Политика хранения (Retention Policy)
RETENTION_DAYS = 90  # Срок хранения обычных файлов в локальном буфере (в днях)

# Параметры сжатия изображений для BLOB-реестра
MAX_IMAGE_WIDTH = 1400
JPEG_QUALITY = 78
SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# Параметры AI-классификации
TRIAGE_MODEL = "gemini-3.1-flash-lite"
PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "triage.txt"

def get_ingress_db_connection():
    """Создает подключение к PostgreSQL от имени изолированного пользователя data_ingress_worker."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
