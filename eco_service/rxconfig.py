import reflex as rx
import os
from dotenv import load_dotenv

# Загрузка переменных окружения (например, подключения к PostgreSQL)
load_dotenv("/home/fujitsu-u745/Projects/eco_service/.env")

config = rx.Config(
    app_name="app",                  # Имя папки приложения внутри проекта
    api_url="http://192.168.43.218:8001",
    backend_host="0.0.0.0",          # Прослушивание всех интерфейсов в WSL
    frontend_host="0.0.0.0",
    backend_port=8001,               # Порт бэкенда
    frontend_port=3001,              # Порт фронтенда
    plugins=[
        rx.plugins.RadixThemesPlugin(),
        rx.plugins.SitemapPlugin(),
    ],
    db_url=os.getenv("DATABASE_URL"),
)