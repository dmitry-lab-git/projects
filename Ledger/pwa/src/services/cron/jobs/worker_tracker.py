import os
import sys
import json
import uuid
import argparse
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv("/home/fujitsu-u745/Projects/secure_folder/pwa/.env")
DB_URL = os.getenv("DATABASE_URL")


def _get_conn():
    if not DB_URL:
        raise RuntimeError("DATABASE_URL не задан в .env")
    return psycopg2.connect(DB_URL, connect_timeout=5)


def start_run(worker_code: str, trigger: str = "SCHEDULED", run_id: str | None = None) -> str:
    """Регистрирует старт воркера и возвращает UUID запуска."""
    run_uuid = run_id or str(uuid.uuid4())
    try:
        with _get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO audit.workers_execution_log (run_id, worker_id, trigger_source, status, started_at)
                SELECT %s::uuid, worker_id, %s, 'RUNNING', NOW()
                FROM audit.workers_registry
                WHERE worker_code = %s;
            """, (run_uuid, trigger, worker_code))
    except Exception as e:
        print(f"[worker_tracker] WARN start_run({worker_code}): {e}", file=sys.stderr)
    return run_uuid


def finish_run(run_id: str, status: str = "SUCCESS", exit_code: int = 0, details: dict | None = None):
    """Фиксирует завершение работы воркера по его UUID."""
    try:
        with _get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                UPDATE audit.workers_execution_log
                SET status = %s,
                    finished_at = NOW(),
                    exit_code = %s,
                    details = COALESCE(details, '{}'::jsonb) || %s::jsonb
                WHERE run_id = %s::uuid;
            """, (status, exit_code, json.dumps(details or {}, ensure_ascii=False), run_id))
    except Exception as e:
        print(f"[worker_tracker] WARN finish_run({run_id}): {e}", file=sys.stderr)


def can_run_debounced(worker_code: str, min_interval_sec: int) -> bool:
    """Замена файлам .last_run: проверяет в БД, прошло ли нужное время с последнего SUCCESS."""
    try:
        with _get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT EXTRACT(EPOCH FROM (NOW() - MAX(l.finished_at)))
                FROM audit.workers_execution_log l
                JOIN audit.workers_registry r ON r.worker_id = l.worker_id
                WHERE r.worker_code = %s AND l.status = 'SUCCESS';
            """, (worker_code,))
            elapsed = cur.fetchone()[0]
            if elapsed is not None and elapsed < min_interval_sec:
                return False
    except Exception as e:
        print(f"[worker_tracker] WARN debounce check({worker_code}): {e}", file=sys.stderr)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI трекер цифровых сотрудников")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_start = sub.add_parser("start")
    p_start.add_argument("worker_code")
    p_start.add_argument("--trigger", default="SCHEDULED")

    p_fin = sub.add_parser("finish")
    p_fin.add_argument("run_id")
    p_fin.add_argument("--status", default="SUCCESS")
    p_fin.add_argument("--code", type=int, default=0)
    p_fin.add_argument("--details", default="{}")

    args = parser.parse_args()
    if args.cmd == "start":
        print(start_run(args.worker_code, args.trigger))
    elif args.cmd == "finish":
        finish_run(args.run_id, args.status, args.code, json.loads(args.details))
