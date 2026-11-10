import reflex as rx
import asyncpg
from app.database.connection import create_database_pool

class BaseState(rx.State):
    """Базовый стейт с доступом к пулу соединений asyncpg."""

    async def get_pool(self) -> asyncpg.Pool:
        """Получает пул соединений напрямую, минуя сохранение в стейте."""
        return await create_database_pool()

class AppState(BaseState):
    """Единый корневой стейт приложения."""
    pass