import reflex as rx
from app.dashboard.states import AppState

def kpi_card(title: str, value: rx.Var, icon: str, color: str) -> rx.Component:
    """Универсальная карточка ключевого показателя эффективности."""
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(title, size="2", color_scheme="gray", weight="medium"),
                rx.heading(value, size="6", weight="bold"),
                spacing="1",
            ),
            rx.spacer(),
            rx.icon(icon, size=28, color=color),
            align="center",
            width="100%",
        ),
        size="2",
        variant="surface",
        width="100%",
    )

def kpi_metrics_grid() -> rx.Component:
    """Сетка KPI карточек на основе витрины v_kpi_summary."""
    return rx.grid(
        kpi_card(
            "Общий вес сырья", 
            rx.cond(AppState.kpi_summary["total_mass_kg"], AppState.kpi_summary["total_mass_kg"].to_string() + " кг", "0 кг"), 
            "scale", 
            "var(--jade-9)"
        ),
        kpi_card(
            "Собрано мешков", 
            rx.cond(AppState.kpi_summary["total_bags_count"], AppState.kpi_summary["total_bags_count"].to_string(), "0"), 
            "package", 
            "var(--blue-9)"
        ),
        kpi_card(
            "Активные общины ( Yards )", 
            rx.cond(AppState.kpi_summary["active_yards_count"], AppState.kpi_summary["active_yards_count"].to_string(), "0"), 
            "map-pin", 
            "var(--orange-9)"
        ),
        kpi_card(
            "Активные операторы", 
            rx.cond(AppState.kpi_summary["active_operators_count"], AppState.kpi_summary["active_operators_count"].to_string(), "0"), 
            "users", 
            "var(--purple-9)"
        ),
        columns="4",
        spacing="4",
        width="100%",
    )