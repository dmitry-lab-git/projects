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


def get_config(project: str) -> DBConfig:
    if not project or not project.strip():
        raise ValueError("Project name must not be empty")

    # 1. Пытаемся достать секреты из Vault
    vault_secrets = get_secrets_for_project(project)

    # 2. Если в Vault пусто, пробуем legacy fallback на .env.<project>
    if not vault_secrets:
        _load_env_file(project)

    prefix = project.upper() + "_"

    # 3. Собираем конфиг. Приоритет: Vault -> os.environ (из .env / окружения) -> дефолт.
    def _get(key: str, default: str | None = None) -> str | None:
        if key in vault_secrets and vault_secrets[key] is not None:
            return str(vault_secrets[key])
        return os.getenv(prefix + key, os.getenv(key, default))

    password = _get("PGPASSWORD")
    if not password:
        raise ValueError(
            f"Missing PGPASSWORD for project '{project}' in Vault and environment"
        )

    return DBConfig(
        host=_get("PGHOST", "localhost") or "localhost",
        port=int(_get("PGPORT", "5432") or "5432"),
        dbname=_get("PGDATABASE", project) or project,
        user=_get("PGUSER", "postgres") or "postgres",
        password=password,
    )