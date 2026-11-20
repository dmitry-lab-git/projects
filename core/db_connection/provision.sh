#!/usr/bin/env bash
set -euo pipefail

PG_HOST="${PG_HOST:-localhost}"
PG_PORT="${PG_PORT:-5432}"

read -r -p "Введите БД: " DB_NAME
read -r -p "Введите пользователя: " DB_USER
read -r -s -p "Введите пароль: " DB_PASSWORD
echo ""
read -r -s -p "Повторите пароль: " DB_PASSWORD_CONFIRM
echo ""

if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
  echo "Ошибка: БД, пользователь и пароль не должны быть пустыми." >&2
  exit 1
fi

if [ "$DB_PASSWORD" != "$DB_PASSWORD_CONFIRM" ]; then
  echo "Ошибка: пароли не совпадают." >&2
  exit 1
fi

SQL_PASS="${DB_PASSWORD//\'/\'\'}"

echo "[1/3] Создаём роль '$DB_USER' и БД '$DB_NAME' в PostgreSQL..."
sudo -u postgres psql -v ON_ERROR_STOP=1 << SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '$DB_USER') THEN
    CREATE ROLE "$DB_USER" LOGIN PASSWORD '$SQL_PASS';
  ELSE
    ALTER ROLE "$DB_USER" WITH LOGIN PASSWORD '$SQL_PASS';
  END IF;
END
\$\$;
SQL

if ! sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1; then
  sudo -u postgres createdb -O "$DB_USER" "$DB_NAME"
fi

sudo -u postgres psql -v ON_ERROR_STOP=1 -d "$DB_NAME" << SQL
GRANT ALL PRIVILEGES ON DATABASE "$DB_NAME" TO "$DB_USER";
GRANT ALL ON SCHEMA public TO "$DB_USER";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "$DB_USER";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "$DB_USER";
SQL

echo "[2/3] Регистрируем проект '$DB_USER' в Vault..."
python3 -m db_connection.vault_cli create-project --project "$DB_USER" --db-name "$DB_NAME" >/dev/null 2>&1 || true

echo "[3/3] Записываем параметры подключения в Vault..."
python3 -m db_connection.vault_cli set --project "$DB_USER" --key PGHOST --value "$PG_HOST" >/dev/null
python3 -m db_connection.vault_cli set --project "$DB_USER" --key PGPORT --value "$PG_PORT" >/dev/null
python3 -m db_connection.vault_cli set --project "$DB_USER" --key PGDATABASE --value "$DB_NAME" >/dev/null
python3 -m db_connection.vault_cli set --project "$DB_USER" --key PGUSER --value "$DB_USER" >/dev/null
python3 -m db_connection.vault_cli set --project "$DB_USER" --key PGPASSWORD --value "$DB_PASSWORD" >/dev/null

echo "Готово: пользователь '$DB_USER' настроен для БД '$DB_NAME'."
