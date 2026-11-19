"""
Загрузчик секретов из vault.secrets для использования в config.py.
"""

from __future__ import annotations

import base64
from pathlib import Path

import psycopg
import yaml

from .vault_crypto import decrypt, make_aad

VAULT_YAML = Path.home() / "Projects/secure_folder/vault.yaml"

# Кэш, чтобы не дёргать БД на каждый запрос конфигурации
_SECRETS_CACHE: dict[str, dict[str, str]] = {}


def _load_yaml() -> dict:
    return yaml.safe_load(VAULT_YAML.read_text())


def get_secrets_for_project(project: str) -> dict[str, str]:
    """
    Возвращает словарь {KEY: VALUE} с расшифрованными секретами для проекта.
    При повторном вызове отдаёт из кэша.
    """
    if project in _SECRETS_CACHE:
        return _SECRETS_CACHE[project]

    if not VAULT_YAML.exists():
        return {}

    vault = _load_yaml()
    m = vault["meta_db"]
    
    try:
        with psycopg.connect(
            host=m["host"], port=m["port"], dbname=m["dbname"],
            user=m["user"], password=m["password"]
        ) as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT key, ciphertext, key_version FROM vault.secrets WHERE project = %s",
                (project,)
            )
            rows = cur.fetchall()
    except Exception:
        # Если база недоступна (или проект не заведён), возвращаем пустой словарь,
        # чтобы config.py мог сделать fallback на .env
        return {}

    if not rows:
        return {}

    keys = vault["master_key"]["keys"]
    secrets_dict = {}

    for k, ciphertext, version in rows:
        b64 = keys.get(version) or keys.get(str(version))
        if not b64:
            continue  # нет такого ключа в yaml (например, старый)
        
        master_key = base64.b64decode(b64)
        aad = make_aad(project, k, version)
        try:
            val = decrypt(master_key, bytes(ciphertext), aad).decode("utf-8")
            secrets_dict[k] = val
        except Exception:
            # Если не удалось расшифровать — пропускаем
            continue

    _SECRETS_CACHE[project] = secrets_dict
    return secrets_dict


def clear_cache() -> None:
    _SECRETS_CACHE.clear()