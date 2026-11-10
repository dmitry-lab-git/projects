import reflex as rx
from .index import index

def register_routes(app: rx.App):
    """Register all application endpoints and dashboard pages."""
    app.add_page(
        index,
        route="/",
        title="EcoService ERP | Dashboard",
    )
