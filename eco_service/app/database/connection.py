from contextlib import asynccontextmanager
import asyncpg
import reflex as rx
from .config import settings

db_pool: asyncpg.Pool | None = None

async def init_db_session(connection: asyncpg.Connection):
    """
    Enforces unified session context parameter locks immediately after connection handshake.
    """
    await connection.execute(f"SET timezone TO '{settings.db_timezone}';")
    await connection.execute(f"SET search_path TO {settings.db_search_path};")

@asynccontextmanager
async def database_lifespan(app: rx.App):
    """
    Manages the lifecycle of the database connection pool.
    """
    global db_pool
    
    # --- DEBUG CONNECTION AND TABLE READ TEST ---
    print("--- [DEBUG] Verifying connection and reading from table ---")
    try:
        test_conn = await asyncpg.connect(settings.database_url)
        # Check actual query execution against the view/table
        row_count = await test_conn.fetchval("SELECT count(*) FROM analytics.v_kpi_summary;")
        print(f"[DEBUG] Success! Table/view is accessible. Row count: {row_count}")
        await test_conn.close()
    except Exception as e:
        print(f"[ERROR] Database table access failed: {e}")
    print("-------------------------------------------------------")

    db_pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=2,
        max_size=10,
        init=init_db_session
    )
    try:
        yield
    finally:
        if db_pool:
            await db_pool.close()
            db_pool = None

async def create_database_pool() -> asyncpg.Pool:
    """
    Adapter for compatibility with states requesting the pool directly.
    """
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=2,
            max_size=10,
            init=init_db_session
        )
    return db_pool

