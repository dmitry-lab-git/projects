import reflex as rx
from .index import index

def register_routes(app: rx.App):
    """Регистрация всех эндпоинтов и страниц дашборда."""
    app.add_page(
        index,
        route="/",
        title="EcoService ERP | Dashboard",
    )