import reflex as rx

@rx.page(route="/", title="EcoService ERP | Главная")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            # Приветственный блок
            rx.vstack(
                rx.heading("Auroville ERP System", size={"initial": "6", "md": "8"}),
                rx.text(
                    "Модульная платформа управления отходами и логистикой пилотного проекта",
                    color_scheme="gray",
                    size={"initial": "3", "md": "4"},
                ),
                spacing="2",
                align="center",
                text_align="center",
                padding_y={"initial": "4", "md": "8"},
            ),
            
            rx.divider(),

            # Карточки быстрого доступа по ролям
            rx.grid(
                # Карточка Сборщика
                rx.card(
                    rx.vstack(
                        rx.icon("truck", size=32, color="var(--jade-9)"),
                        rx.heading("Сборщик", size="5"),
                        rx.text(
                            "Регистрация вывоза отходов с площадок (Yards), выбор типа мешка и транспорта.",
                            size="2", color_scheme="gray",
                        ),
                        rx.spacer(),
                        rx.link(
                            rx.button("Открыть портал", color_scheme="jade", size="3", width="100%"),
                            href="/collector",
                            width="100%",
                        ),
                        spacing="4", height="100%",
                    ),
                    size="3",
                ),
                
                # Карточка Сортировщика
                rx.card(
                    rx.vstack(
                        rx.icon("scale", size=32, color="var(--blue-9)"),
                        rx.heading("Сортировщик", size="5"),
                        rx.text(
                            "Взвешивание мешков по ID, распределение по фракциям и контроль загрязнений.",
                            size="2", color_scheme="gray",
                        ),
                        rx.spacer(),
                        rx.link(
                            rx.button("Открыть портал", color_scheme="blue", size="3", width="100%"),
                            href="/sorter",
                            width="100%",
                        ),
                        spacing="4", height="100%",
                    ),
                    size="3",
                ),
                
                # Карточка Менеджера
                rx.card(
                    rx.vstack(
                        rx.icon("layout-dashboard", size=32, color="var(--amber-9)"),
                        rx.heading("Менеджер / CEO", size="5"),
                        rx.text(
                            "Аналитические дашборды, мониторинг потоков отходов, KPI и отчеты по персоналу.",
                            size="2", color_scheme="gray",
                        ),
                        rx.spacer(),
                        rx.link(
                            rx.button("Открыть панель", color_scheme="amber", size="3", width="100%"),
                            href="/manager",
                            width="100%",
                        ),
                        spacing="4", height="100%",
                    ),
                    size="3",
                ),
                
                columns={"initial": "1", "md": "3"},
                spacing={"initial": "4", "md": "6"},
                width="100%",
                padding_y="4",
            ),
            
            spacing={"initial": "4", "md": "6"},
            width="100%",
            align="center",
        ),
        max_width="1200px",
        padding={"initial": "2", "md": "4"},
    )