import asyncpg
from config import settings

async def init_db_session(connection: asyncpg.Connection):
    """
    Enforces unified session context parameter locks immediately after connection handshake.
    Guarantees cross-environment independence from host OS locale/timezone setups.
    """
    await connection.execute(f"SET timezone TO '{settings.db_timezone}';")
    await connection.execute(f"SET search_path TO {settings.db_search_path};")

async def create_database_pool() -> asyncpg.Pool:
    """
    Initializes a highly performant asynchronous connection pool 
    with injection of global contextual session init queries.
    """
    return await asyncpg.create_pool(
        dsn=settings.database_dsn,
        min_size=2,
        max_size=10,
        init=init_db_session
    )
