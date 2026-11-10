import reflex as rx
from app.states.analytics import AnalyticsState
from app.states.auth import AuthState

def kpi_card(title: str, value: rx.Var, icon: str, color: str = "jade") -> rx.Component:
    """Key Performance Indicator (KPI) card component bound to dynamic data."""
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
            rx.heading("Community Yard Performance", size={"initial": "3", "md": "4"}),
            rx.text("Total mass collected and bag counts by collection points", size="2", color_scheme="gray"),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Community / Yard", class_name="sticky-th"),
                            rx.table.column_header_cell("Address", class_name="sticky-th"),
                            rx.table.column_header_cell("Bags Received", class_name="sticky-th"),
                            rx.table.column_header_cell("Total Weight (kg)", class_name="sticky-th"),
                            rx.table.column_header_cell("Avg Bag Weight (kg)", class_name="sticky-th"),
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
    """Waste breakdown table by fractions with a sticky header on scroll."""
    return rx.card(
        rx.vstack(
            rx.heading("Waste Structure by Fractions", size={"initial": "3", "md": "4"}),
            rx.text("Breakdown by categories, codes, weight, bags, and percentages", size="2", color_scheme="gray"),
            rx.text("↔ Scroll horizontally to view all data", size="1", color_scheme="gray", weight="medium"),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Code", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Material Fraction", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Bags", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Total Weight (kg)", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Share (%)", class_name="sticky-table-header"),
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
    """Operator performance monitoring table with a sticky header on scroll."""
    return rx.card(
        rx.vstack(
            rx.heading("Operator Performance", size={"initial": "3", "md": "4"}),
            rx.text("Field staff operations activity logs and throughput volume", size="2", color_scheme="gray"),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Operator", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Role", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Event Type", class_name="sticky-table-header"),
                            rx.table.column_header_cell("Operations", class_name="sticky-table-header"),
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
    """Bar chart demonstrating collection trends over the past week."""
    return rx.card(
        rx.vstack(
            rx.heading("Collection Trends (Past Week)", size={"initial": "3", "md": "4"}),
            rx.text("Daily mass intake in kilograms", size="2", color_scheme="gray"),
            rx.spacer(),
            rx.box(
                rx.recharts.bar_chart(
                    rx.recharts.bar(
                        data_key="daily_weight_kg", 
                        fill="var(--jade-9)", 
                        name="Weight (kg)",
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
    title="EcoService ERP | Manager Dashboard", 
    on_load=[AnalyticsState.fetch_analytics_data]
)
def manager_page() -> rx.Component:
    """Manager management dashboard containing core waste stream analytics."""
    return rx.container(
        rx.vstack(
            # Page header section
            rx.flex(
                rx.vstack(
                    rx.heading(
                        "Manager Management Dashboard", 
                        size={"initial": "5", "md": "7"}, 
                        text_align={"initial": "center", "md": "left"}
                    ),
                    rx.text(
                        "Real-time tracking of waste streams, yard efficiency, and operator throughput",
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
                        # DB connection failure alert
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
                        # KPI Summary Grid
                        rx.grid(
                        kpi_card(
                        "Total Mass (kg)",
                        AnalyticsState.kpi_summary["total_weight_kg"].to_string(),
                        "scale",
                        "amber"
                        ),
                        kpi_card(
                        "Total Bags",
                        AnalyticsState.kpi_summary["total_bags_registered"].to_string(),
                        "recycle",
                        "blue"
                        ),
                        kpi_card(
                        "Active Yards",
                        AnalyticsState.kpi_summary["active_yards_count"].to_string(),
                        "map-pin",
                        "jade"
                        ),
                        kpi_card(
                        "Avg Bag Weight (kg)",
                        AnalyticsState.kpi_summary["avg_bag_weight_kg"].to_string(),
                        "trending-up",
                        "green"
                        ),
                        columns={"initial": "1", "sm": "2", "md": "4"},
                        spacing="4",
                        width="100%",
                        ),
                        # Analytics views with dynamic loading conditional spinner
                        rx.cond(
                        AnalyticsState.is_loading,
                        rx.flex(
                        rx.spinner(size="3"),
                        rx.text("Loading data from database..."),
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