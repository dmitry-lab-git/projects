import reflex as rx
from app.database import database_lifespan

# Импортируем страницы из реальной структуры папок (app/dashboard/pages/)
import app.dashboard.pages.index
import app.dashboard.pages.collector.index
import app.dashboard.pages.sorter.index
import app.dashboard.pages.manager.index

# Инициализация приложения Reflex
app = rx.App()

# Регистрация единого контекстного менеджера жизненного цикла базы данных
app.register_lifespan_task(database_lifespan)