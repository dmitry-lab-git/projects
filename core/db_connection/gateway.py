from typing import Any

from .connection import get_cursor


def ping_project(project: str) -> dict[str, Any]:
    with get_cursor(project) as cur:
        cur.execute("SELECT 1 AS ok, now() AS server_time")
        row = cur.fetchone()
    return {
        "project": project,
        "db_ok": bool(row[0]) if row else False,
        "server_time": row[1].isoformat() if row and row[1] is not None else None,
    }
