import reflex as rx
from app.database import database_lifespan

# Import pages from the actual directory structure (app/dashboard/pages/)
import app.dashboard.pages.index
import app.dashboard.pages.collector.index
import app.dashboard.pages.sorter.index
import app.dashboard.pages.manager.index

# Initialize the Reflex application
app = rx.App()

# Register a single unified database lifecycle lifespan task manager
app.register_lifespan_task(database_lifespan)
