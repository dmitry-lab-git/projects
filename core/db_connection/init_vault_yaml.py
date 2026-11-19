"""
Создание ~/Projects/secure_folder/vault.yaml.

Содержит:
  - подключение к platform_meta (vault_reader + пароль)
  - мастер-ключ (base64 32 байта) + active_version

Права на файл — 0600. Существующий файл не перезаписывается
без --force (иначе легко стереть мастер-ключ и потерять секреты).
"""

from __future__ import annotations

import argparse
import base64
import getpass
import os
import sys
import tempfile
from pathlib import Path

import yaml

VAULT_YAML = Path.home() / "Projects/secure_folder/vault.yaml"


def _write_atomic(data: dict) -> None:
    d = VAULT_YAML.parent
    d.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, prefix=".vault.", suffix=".tmp")
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
        os.replace(tmp, VAULT_YAML)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=5432)
    ap.add_argument("--dbname", default="platform_meta")
    ap.add_argument("--user", default="vault_reader")
    ap.add_argument("--password", default=None,
                    help="если не задан — спросит интерактивно")
    ap.add_argument("--force", action="store_true",
                    help="перезаписать существующий vault.yaml")
    args = ap.parse_args(argv)

    if VAULT_YAML.exists() and not args.force:
        sys.exit(
            f"{VAULT_YAML} уже существует.\n"
            f"Перезапись уничтожит мастер-ключ и все секреты в БД "
            f"станут нечитаемыми.\n"
            f"Если уверен — запусти с --force."
        )

    password = args.password
    if password is None:
        password = getpass.getpass("vault_reader password: ")
    if not password:
        sys.exit("empty password")

    master_key = os.urandom(32)
    b64 = base64.b64encode(master_key).decode("ascii")

    data = {
        "version": 1,
        "meta_db": {
            "host": args.host,
            "port": args.port,
            "dbname": args.dbname,
            "user": args.user,
            "password": password,
        },
        "master_key": {
            "active_version": 1,
            "keys": {1: b64},
        },
    }

    _write_atomic(data)

    mode = VAULT_YAML.stat().st_mode & 0o777
    if mode != 0o600:
        sys.exit(f"wrong permissions after write: {oct(mode)}")

    print(f"written: {VAULT_YAML}  (mode {oct(mode)})")
    print(f"active master key version: 1")
    print(f"master key (base64): {b64}")
    print()
    print("Мастер-ключ показан один раз. Он уже в vault.yaml.")
    print("Если потеряешь vault.yaml — секреты в vault.secrets")
    print("станут нечитаемыми.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())