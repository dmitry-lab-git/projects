"""
CLI для управления секретами в vault.secrets.

Минимальный набор на этом шаге:
    set    — положить секрет (project, key, value) в vault.secrets
    list   — показать ключи проекта (без расшифровки)
    get    — показать расшифрованное значение (для отладки)

Использование:
    python -m core.db_connection.vault_cli set \
        --project traffic_tracker --key PGPASSWORD --generate

    python -m core.db_connection.vault_cli set \
        --project traffic_tracker --key PGHOST --value localhost

    python -m core.db_connection.vault_cli list --project traffic_tracker
    python -m core.db_connection.vault_cli get  --project traffic_tracker --key PGPASSWORD
"""

from __future__ import annotations

import argparse
import base64
import getpass
import os
import secrets
import sys
from pathlib import Path

import psycopg
import yaml

from .vault_crypto import decrypt, encrypt, make_aad

VAULT_YAML = Path.home() / "Projects/secure_folder/vault.yaml"


# ---------- bootstrap ----------

def load_vault_yaml() -> dict:
    if not VAULT_YAML.exists():
        sys.exit(f"vault.yaml not found: {VAULT_YAML}")
    st = VAULT_YAML.stat()
    if (st.st_mode & 0o777) != 0o600:
        sys.exit(f"{VAULT_YAML} has mode {oct(st.st_mode & 0o777)}, expected 0600")
    return yaml.safe_load(VAULT_YAML.read_text())


def get_active_key(vault: dict) -> tuple[int, bytes]:
    mk = vault["master_key"]
    version = int(mk["active_version"])
    keys = mk["keys"]
    if version not in keys and str(version) not in keys:
        sys.exit(f"active_version={version} missing in master_key.keys")
    b64 = keys.get(version) or keys.get(str(version))
    return version, base64.b64decode(b64)


def connect_meta(vault: dict, admin: bool = False) -> psycopg.Connection:
    if admin:
        m = vault.get("meta_admin_db")
        if not m:
            sys.exit("meta_admin_db not found in vault.yaml — required for write operations")
    else:
        m = vault["meta_db"]
        
    return psycopg.connect(
        host=m["host"], port=m["port"], dbname=m["dbname"],
        user=m["user"], password=m["password"],
    )


# ---------- commands ----------

def cmd_set(args) -> int:
    vault = load_vault_yaml()
    version, master_key = get_active_key(vault)

    if args.value is not None and args.generate:
        sys.exit("--value and --generate are mutually exclusive")

    if args.generate:
        value = secrets.token_urlsafe(32)
        print(f"generated value for {args.project}.{args.key}: {value}")
    elif args.value is not None:
        value = args.value
    else:
        value = getpass.getpass(f"value for {args.project}.{args.key}: ")
    if not value:
        sys.exit("empty value")

    aad = make_aad(args.project, args.key, version)
    blob = encrypt(master_key, value.encode("utf-8"), aad)

    with connect_meta(vault, admin=True) as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO vault.secrets
                (project, key, ciphertext, key_version, updated_at)
            VALUES (%s, %s, %s, %s, now())
            ON CONFLICT (project, key) DO UPDATE
               SET ciphertext  = EXCLUDED.ciphertext,
                   key_version = EXCLUDED.key_version,
                   updated_at  = now()
        """, (args.project, args.key, blob, version))
        cur.execute("""
            INSERT INTO vault.audit_log
                (project, key, action, actor, success)
            VALUES (%s, %s, 'write', %s, true)
        """, (args.project, args.key, f"{os.getenv('USER', 'unknown')}:{os.uname().nodename}"))
        conn.commit()

    print(f"set {args.project}.{args.key} (key_version={version})")
    return 0


def cmd_list(args) -> int:
    vault = load_vault_yaml()
    with connect_meta(vault) as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT project, key, key_version, updated_at
              FROM vault.secrets
             WHERE (%s::text IS NULL OR project = %s)
             ORDER BY project, key
        """, (args.project, args.project))
        rows = cur.fetchall()
    if not rows:
        print("(no secrets)")
        return 0
    print(f"{'project':<25} {'key':<18} {'ver':>3}  updated_at")
    for project, key, ver, ts in rows:
        print(f"{project:<25} {key:<18} {ver:>3}  {ts.isoformat()}")
    return 0


def cmd_get(args) -> int:
    vault = load_vault_yaml()
    with connect_meta(vault) as conn, conn.cursor() as cur:
        cur.execute("""
            SELECT ciphertext, key_version
              FROM vault.secrets
             WHERE project = %s AND key = %s
        """, (args.project, args.key))
        row = cur.fetchone()
    if row is None:
        sys.exit(f"not found: {args.project}.{args.key}")

    ciphertext, version = row
    keys = vault["master_key"]["keys"]
    b64 = keys.get(version) or keys.get(str(version))
    if b64 is None:
        sys.exit(f"key_version={version} missing in vault.yaml")
    master_key = base64.b64decode(b64)

    aad = make_aad(args.project, args.key, version)
    value = decrypt(master_key, bytes(ciphertext), aad).decode("utf-8")
    print(value)
    return 0

def cmd_create_project(args) -> int:
    vault = load_vault_yaml()
    with connect_meta(vault, admin=True) as conn, conn.cursor() as cur:
        # Проверяем, есть ли проект
        cur.execute("SELECT 1 FROM vault.projects WHERE project = %s", (args.project,))
        if cur.fetchone():
            print(f"project {args.project!r} already exists — skip")
            return 0
            
        cur.execute("""
            INSERT INTO vault.projects (project, db_name, is_active)
            VALUES (%s, %s, true)
        """, (args.project, args.db_name or args.project))
        cur.execute("""
            INSERT INTO vault.audit_log (project, action, actor, success)
            VALUES (%s, 'create_project', %s, true)
        """, (args.project, f"{os.getenv('USER', 'unknown')}:{os.uname().nodename}"))
        conn.commit()
    print(f"created project {args.project!r} (db: {args.db_name or args.project})")
    return 0


# ---------- main ----------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="vault_cli")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_set = sub.add_parser("set")
    p_set.add_argument("--project", required=True)
    p_set.add_argument("--key", required=True)
    g = p_set.add_mutually_exclusive_group()
    g.add_argument("--value", default=None)
    g.add_argument("--generate", action="store_true")
    p_set.set_defaults(func=cmd_set)

    p_list = sub.add_parser("list")
    p_list.add_argument("--project", default=None)
    p_list.set_defaults(func=cmd_list)

    p_get = sub.add_parser("get")
    p_get.add_argument("--project", required=True)
    p_get.add_argument("--key", required=True)
    p_get.set_defaults(func=cmd_get)
  
    p_create = sub.add_parser("create-project")
    p_create.add_argument("--project", required=True)
    p_create.add_argument("--db-name", default=None, help="имя БД (по умолчанию = project)")
    p_create.set_defaults(func=cmd_create_project)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())