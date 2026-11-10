import reflex as rx
from app.states.analytics import AnalyticsState
from app.states.auth import AuthState

def kpi_card(title: str, value: rx.Var, icon: str, color: str = "jade") -> rx.Component:
    """Компонент карточки ключевого показателя (KPI) с привязкой к динамическим данным."""
    return rx.card(
        rx.hstack(
            rx.icon(icon, size=28, color=rx.color(color, 9)),
            rx.vstack(
                rx.text(title, size="2", color_scheme="gray"),
                rx.heading(value, size={"initial": "5", "md": "6"}),
                spacing="1",
            ),
            spacing="4",
            align="center",
        ),
        size="2",
        variant="surface",
    )

def yard_performance_table() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Эффективность общин (Yards)", size={"initial": "3", "md": "4"}),
            rx.text("Общий объем собранного сырья и количество мешков по точкам", size="2", color_scheme="gray"),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Община / Ярд", class_name="sticky-th"),
                            rx.table.column_header_cell("Адрес", class_name="sticky-th"),
                            rx.table.column_header_cell("Мешков получено", class_name="sticky-th"),
                            rx.table.column_header_cell("Общий вес (кг)", class_name="sticky-th"),
                            rx.table.column_header_cell("Ср. вес мешка (кг)", class_name="sticky-th"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            AnalyticsState.yard_performance,
                            lambda yard: rx.table.row(
                                rx.table.cell(yard["yard_name"], weight="bold"),
                                rx.table.cell(yard["address"]),
                                rx.table.cell(yard["total_bags_received"].to_string()),
                                rx.table.cell(yard["total_weight_kg"].to_string()),
                                rx.table.cell(yard["avg_bag_weight_kg"].to_string()),
                            ),
                        )
                    ),
                    variant="surface",
                    width="100%",
                ),
                class_name="table-scroll-container",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        width="100%",
    )

def waste_category_table() -> rx.Component:
    """Таблица структуры отходов по фракциям с закреплением шапки при скролле."""
    return rx.card(
        rx.vstack(
            rx.heading("Структура отходов по фракциям", size={"initial": "3", "md": "4"}),
            rx.text("Детализация по фракциям, кодам, весу, мешкам и долям", size="2", color_scheme="gray"),
            rx.text("↔ Прокрутите таблицу вбок для просмотра всех данных", size="1", color_scheme="gray", weight="medium"),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Код", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Категория фракции", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Мешков", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Общий вес (кг)", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Доля (%)", class_name="sticky-table-header"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            AnalyticsState.waste_by_category,
                            lambda cat: rx.table.row(
                                rx.table.cell(cat["category_code"]),
                                rx.table.cell(cat["category_name"], weight="bold"),
                                rx.table.cell(cat["bag_count"].to_string()),
                                rx.table.cell(cat["total_weight_kg"].to_string()),
                                rx.table.cell(cat["weight_percentage"].to_string() + " %"),
                            ),
                        )
                    ),
                    variant="surface",
                    width="100%",
                ),
                class_name="table-scroll-container",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        width="100%",
    )


def operator_performance_table() -> rx.Component:
    """Таблица производительности операторов с закреплением шапки при скролле."""
    return rx.card(
        rx.vstack(
            rx.heading("Производительность операторов", size={"initial": "3", "md": "4"}),
            rx.text("Активность полевых сотрудников и объем операций", size="2", color_scheme="gray"),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Оператор", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Роль", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Событие", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Операций", class_name="sticky-table-header"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            AnalyticsState.operator_performance,
                            lambda op: rx.table.row(
                                rx.table.cell(op["full_name"], weight="bold"),
                                rx.table.cell(rx.text(op["role"], truncate=True, max_width="110px")),
                                rx.table.cell(rx.text(op["event_type_handled"], truncate=True, max_width="130px")),
                                rx.table.cell(op["operations_count"].to_string()),
                            ),
                        )
                    ),
                    variant="surface",
                    width="100%",
                ),
                class_name="table-scroll-container",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        width="100%",
    )

def waste_trend_chart() -> rx.Component:
    """Столбчатая диаграмма динамики сбора отходов за последнюю неделю с точными отступами."""
    return rx.card(
        rx.vstack(
            rx.heading("Динамика сбора за последнюю неделю", size={"initial": "3", "md": "4"}),
            rx.text("Поступление веса (кг) по дням", size="2", color_scheme="gray"),
            rx.spacer(),
            rx.box(
                rx.recharts.bar_chart(
                    rx.recharts.bar(
                        data_key="daily_weight_kg", 
                        fill="var(--jade-9)", 
                        name="Вес (кг)",
                    ),
                    rx.recharts.x_axis(data_key="log_date"),
                    rx.recharts.y_axis(width=30),
                    rx.recharts.tooltip(),
                    rx.recharts.legend(),
                    data=AnalyticsState.daily_trends,
                    height=280,
                    width="100%",
                    margin={"top": 10, "right": 10, "left": -25, "bottom": 0},
                ),
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        width="100%",
    )


@rx.page(
    route="/manager",
    title="EcoService ERP | Панель менеджера", 
    on_load=[AnalyticsState.fetch_analytics_data]
)
def manager_page() -> rx.Component:
    """Панель управления менеджера с аналитикой системы управления отходами."""
    return rx.container(
        rx.vstack(
            # Шапка страницы с выверенными отступами (как в index_5.py)
            rx.flex(
                rx.vstack(
                    rx.heading(
                        "Панель управления менеджера", 
                        size={"initial": "5", "md": "7"}, 
                        text_align={"initial": "center", "md": "left"}
                    ),
                    rx.text(
                        "Оперативный контроль потоков, площадок и эффективности персонала",
                        color_scheme="gray",
                        size={"initial": "2", "md": "3"},
                        text_align={"initial": "center", "md": "left"},
                    ),
                    spacing="1",
                    align={"initial": "center", "md": "start"},
                    width="100%",
                ),
                rx.hstack(
                    rx.badge(
                        rx.hstack(
                            rx.icon("user", size=14),
                            rx.text(AuthState.user_role),
                        ),
                        color_scheme="amber",
                        size="2",
                    ),
                    rx.link(
                        rx.button(
                            rx.icon("layout-dashboard", size=16),
                            "Back",
                            variant="soft",
                            size="2",
                        ),
                        href="/",
                    ),
                    rx.button(
                        rx.icon("refresh-cw", size=16),
                        "Refresh",
                        on_click=AnalyticsState.fetch_analytics_data,
                        loading=AnalyticsState.is_loading,
                        color_scheme="amber",
                        variant="soft",
                        size="2",
                    ),
                    align="center",
                    spacing="2",
                    justify={"initial": "center", "md": "end"},
                    width={"initial": "100%", "md": "auto"},
                ),
                direction={"initial": "column", "md": "row"},
                justify="between",
                align="center",
                width="100%",
                padding_top="2",
                padding_bottom="2",
                gap="4",
            ),
            rx.divider(),

            # Сообщение об ошибке, если БД недоступна
            rx.cond(
                AnalyticsState.error_message != "",
                rx.callout.root(
                    rx.callout.icon(rx.icon("circle_help")),
                    rx.callout.text(AnalyticsState.error_message),
                    color_scheme="red",
                    role="alert",
                    width="100%",
                ),
            ),

            # Блок KPI карточек
            rx.grid(
                kpi_card(
                    "Всего собрано (кг)", 
                    AnalyticsState.kpi_summary["total_weight_kg"].to_string(), 
                    "scale", 
                    "amber"
                ),
                kpi_card(
                    "Всего мешков", 
                    AnalyticsState.kpi_summary["total_bags_registered"].to_string(), 
                    "recycle", 
                    "blue"
                ),
                kpi_card(
                    "Активные площадки", 
                    AnalyticsState.kpi_summary["active_yards_count"].to_string(), 
                    "map-pin", 
                    "jade"
                ),
                kpi_card(
                    "Средний вес мешка (кг)", 
                    AnalyticsState.kpi_summary["avg_bag_weight_kg"].to_string(), 
                    "trending-up", 
                    "green"
                ),
                columns={"initial": "1", "sm": "2", "md": "4"},
                spacing="4",
                width="100%",
            ),

            # Секция оперативных витрин с индикатором загрузки
            rx.cond(
                AnalyticsState.is_loading,
                rx.flex(
                    rx.spinner(size="3"),
                    rx.text("Загрузка данных из БД..."),
                    spacing="3",
                    align="center",
                    padding_y="4",
                ),
                rx.vstack(
                    waste_trend_chart(),
                    operator_performance_table(),
                    waste_category_table(),
                    yard_performance_table(),
                    spacing="6",
                    width="100%",
                ),
            ),
            
            spacing={"initial": "4", "md": "6"}, 
            width="100%", 
            padding={"initial": "2", "md": "4"},
        ),
        max_width="1200px",
    )