import reflex as rx
from app.dashboard.states import AppState

def waste_trend_chart() -> rx.Component:
    """График суточных трендов сбора отходов (LineChart)."""
    return rx.card(
        rx.vstack(
            rx.heading("Суточная динамика сбора отходов (кг)", size="4"),
            rx.text("Динамика поступления сырья за последние дни", size="2", color_scheme="gray"),
            rx.spacer(),
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="organic_kg", 
                    stroke="var(--green-9)", 
                    name="Органика"
                ),
                rx.recharts.line(
                    data_key="clean_dry_kg", 
                    stroke="var(--blue-9)", 
                    name="Чистый сухой"
                ),
                rx.recharts.line(
                    data_key="dirty_mixed_kg", 
                    stroke="var(--tomato-9)", 
                    name="Смешанный"
                ),
                rx.recharts.x_axis(data_key="trend_date"),
                rx.recharts.y_axis(),
                rx.recharts.tooltip(),
                rx.recharts.legend(),
                data=AppState.daily_trends,
                height=300,
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        width="100%",
    )


def waste_category_pie_chart() -> rx.Component:
    """Круговая диаграмма структуры отходов по категориям (PieChart)."""
    return rx.card(
        rx.vstack(
            rx.heading("Структура отходов по фракциям", size="4"),
            rx.text("Процентное соотношение собранных категорий", size="2", color_scheme="gray"),
            rx.spacer(),
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    data=AppState.waste_by_category,
                    data_key="total_weight_kg",
                    name_key="category_name",
                    cx="50%",
                    cy="50%",
                    outer_radius=100,
                    fill="var(--jade-9)",
                    label=True,
                ),
                rx.recharts.tooltip(),
                height=300,
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        size="3",
        width="100%",
    )


def analytics_charts_grid() -> rx.Component:
    """Сетка графиков аналитики."""
    return rx.grid(
        waste_trend_chart(),
        waste_category_pie_chart(),
        columns="2",
        spacing="4",
        width="100%",
    )