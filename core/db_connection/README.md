# db_connection

Shared PostgreSQL connection layer for all projects under `~/Projects`.

Design principle: no module opens a database connection directly.
All database access goes through this package. A connection pool is
created once per project and reused for the lifetime of the process.

## Structure

core/db_connection/
  README.md         # This document
  __init__.py       # Public API: get_conn, get_cursor, get_pool
  config.py         # Environment configuration (DB + legacy .env)
  connection.py     # Connection pool management, one pool per project
  vault_loader.py   # Decrypts and loads secrets from platform_meta
  vault_crypto.py   # AES-GCM encryption/decryption
  vault_cli.py      # CLI for managing secrets and projects

## Credentials Architecture

We use a hybrid approach. New projects store credentials encrypted in the
`platform_meta` database. Legacy projects still use `.env` files until
they are migrated.

### 1. New Projects (Vault)
Credentials are stored in `platform_meta` DB (schema `vault`). They are
encrypted using AES-GCM with a master key stored in:
`~/Projects/secure_folder/vault.yaml`

Security Model:
- `vault_admin`: Used ONLY by `vault_cli.py`. Can create projects and modify secrets.
- `vault_reader`: Used by applications. Read-only access. Cannot modify secrets.

### 2. Legacy Projects (Fallback)
If a project is not found in the Vault DB, `config.py` falls back to reading:
`~/Projects/secure_folder/vpn-dmitry-lab/.env.<project>`

Example `.env.household`:
HOUSEHOLD_PGHOST=localhost
HOUSEHOLD_PGPORT=5432
HOUSEHOLD_PGDATABASE=household
HOUSEHOLD_PGUSER=postgres
HOUSEHOLD_PGPASSWORD=***

Resolution order for each setting:
1. Vault DB (if project exists there)
2. Project-prefixed variable from `.env`, e.g. `HOUSEHOLD_PGHOST`
3. Unprefixed variable from `.env`, e.g. `PGHOST`
4. Built-in default, e.g. `localhost`, `5432`

## Usage

from core.db_connection import get_cursor, get_conn

# Read query, auto-commit on context exit
with get_cursor("household") as cur:
    cur.execute("SELECT now()")
    print(cur.fetchone())

# Different project, different database, different pool
with get_cursor("traffic_tracker") as cur:
    cur.execute("SELECT 1")

Semantics:
- `get_cursor(project)` yields a cursor, commits on successful exit,
  rolls back on exception, and returns the connection to the pool.
- `get_conn(project)` yields a connection without automatic commit.

## Integration with External Projects

If your project is located outside `~/Projects/core`, you need to install the `core` package into your project's virtual environment.

1. Ensure `~/Projects/core/pyproject.toml` exists (see above).
2. Activate your project's venv:
   ```bash
   source ~/Projects/<your_project>/venv/bin/activate


## Adding a New Project (Регламент)

Начиная с версии 2.0, секреты новых проектов хранятся в зашифрованном виде в служебной БД `platform_meta`. Файлы `.env` для новых проектов **не создаются**.

### Шаг 1. Создать проект в реестре

```bash
python -m core.db_connection.vault_cli create-project --project <имя_проекта>