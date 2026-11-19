from contextlib import contextmanager
from psycopg_pool import ConnectionPool
from .config import get_config

_pools: dict[str, ConnectionPool] = {}

def get_pool(project: str = "household") -> ConnectionPool:
    if project not in _pools:
        cfg = get_config(project)
        _pools[project] = ConnectionPool(
            conninfo=f"host={cfg.host} port={cfg.port} dbname={cfg.dbname} user={cfg.user} password={cfg.password}",
            min_size=1, max_size=5, open=True,
        )
    return _pools[project]

@contextmanager
def get_conn(project: str = "household"):
    with get_pool(project).connection() as conn:
        yield conn

@contextmanager
def get_cursor(project: str = "household"):
    with get_conn(project) as conn:
        with conn.cursor() as cur:
            yield cur
            conn.commit()