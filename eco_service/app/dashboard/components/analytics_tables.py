import reflex as rx
from app.states.analytics import AppState

def yard_performance_table() -> rx.Component:
    """Таблица эффективности общин / точек сбора (v_yard_performance)."""
    return rx.card(
        rx.vstack(
            rx.heading("Эффективность общин (Yards)", size="4"),
            rx.text("Общий объем собранного сырья и количество мешков по точкам", size="2", color_scheme="gray"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Община / Ярд"),
                        rx.table.column_header_cell("Всего вес (кг)"),
                        rx.table.column_header_cell("Мешков"),
                        rx.table.column_header_cell("Последний сбор"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        AppState.yard_performance,
                        lambda yard: rx.table.row(
                            rx.table.cell(yard["yard_name"], weight="bold"),
                            rx.table.cell(yard["total_weight_kg"].to_string()),
                            rx.table.cell(yard["bags_count"].to_string()),
                            rx.table.cell(yard["last_collection_at"].to_string()),
                        ),
                    )
                ),
                variant="surface",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        width="100%",
    )


def operator_performance_table() -> rx.Component:
    """Таблица производительности операторов (v_operator_performance)."""
    return rx.card(
        rx.vstack(
            rx.heading("Производительность операторов", size="4"),
            rx.text("Активность полевых сотрудников и объем отсортированного сырья", size="2", color_scheme="gray"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Оператор"),
                        rx.table.column_header_cell("Роль"),
                        rx.table.column_header_cell("Событий"),
                        rx.table.column_header_cell("Отсортировано (кг)"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        AppState.operator_performance,
                        lambda op: rx.table.row(
                            rx.table.cell(op["full_name"], weight="bold"),
                            rx.table.cell(op["role"]),
                            rx.table.cell(op["events_count"].to_string()),
                            rx.table.cell(op["total_sorted_kg"].to_string()),
                        ),
                    )
                ),
                variant="surface",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        width="100%",
    )


def analytics_tables_grid() -> rx.Component:
    """Сетка таблиц аналитики."""
    return rx.grid(
        yard_performance_table(),
        operator_performance_table(),
        columns="2",
        spacing="4",
        width="100%",
    )