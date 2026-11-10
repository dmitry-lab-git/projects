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
    Управляет жизненным циклом пула соединений с БД.
    """
    global db_pool
    
    # --- ОТЛАДОЧНЫЙ ТЕСТ ПОДКЛЮЧЕНИЯ И ТАБЛИЦЫ ---
    print("--- [DEBUG] Проверка подключения и чтения из таблицы ---")
    try:
        test_conn = await asyncpg.connect(settings.database_url)
        # Проверяем реальный запрос к представлению/таблице
        row_count = await test_conn.fetchval("SELECT count(*) FROM analytics.v_kpi_summary;")
        print(f"[DEBUG] Успешно! Таблица/представление доступно. Количество строк: {row_count}")
        await test_conn.close()
    except Exception as e:
        print(f"[ERROR] Ошибка доступа к таблице БД: {e}")
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
    Адаптер для совместимости со стейтами, запрашивающими пул напрямую.
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