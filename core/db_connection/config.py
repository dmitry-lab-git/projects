import os
from dataclasses import dataclass
from pathlib import Path

from .vault_loader import get_secrets_for_project

SECURE_DIR = Path.home() / "Projects/secure_folder/vpn-dmitry-lab"

def _load_env_file(project: str) -> None:
    path = SECURE_DIR / f".env.{project}"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

@dataclass(frozen=True)
class DBConfig:
    host: str
    port: int
    dbname: str
    user: str
    password: str

def get_config(project: str = "household") -> DBConfig:
    # 1. Пытаемся достать из новой БД
    vault_secrets = get_secrets_for_project(project)
    
    # 2. Если в БД пусто, делаем старый fallback на .env (на время миграции)
    if not vault_secrets:
        _load_env_file(project)

    prefix = project.upper() + "_"
    
    # 3. Собираем конфиг. Приоритет: БД -> os.environ (из .env) -> дефолт.
    def _get(key: str, default: str) -> str:
        if key in vault_secrets:
            return vault_secrets[key]
        return os.getenv(prefix + key, os.getenv(key, default))

    return DBConfig(
        host=_get("PGHOST", "localhost"),
        port=int(_get("PGPORT", "5432")),
        dbname=_get("PGDATABASE", project),
        user=_get("PGUSER", "postgres"),
        password=_get("PGPASSWORD", ""),
    )