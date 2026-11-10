import reflex as rx

class CollectorState(rx.State):
    yard_id: str = "Central Yard"
    bag_type: str = "ORGANIC"
    transport: str = "rickshaw"
    is_submitting: bool = False
    message: str = ""

    # Явные сеттеры для полей формы (устраняют AttributeError)
    def set_yard_id(self, value: str):
        self.yard_id = value

    def set_bag_type(self, value: str):
        self.bag_type = value

    def set_transport(self, value: str):
        self.transport = value

    async def submit_collection(self):
        self.is_submitting = True
        # Логика записи в БД для сборщика
        self.message = "Вывоз успешно зарегистрирован!"
        self.is_submitting = False

@rx.page(route="/collector", title="EcoService ERP | Сборщик")
def collector_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Портал сборщика (COLLECTOR)", size={"initial": "5", "md": "7"}),
            rx.text("Регистрация поступления мешков с площадок", color_scheme="gray", size={"initial": "2", "md": "3"}),
            rx.divider(),
            
            rx.card(
                rx.vstack(
                    rx.text("Площадка сбора (Yard)", weight="bold", size="2"),
                    rx.select(
                        ["Central Yard", "Solar Kitchen Yard", "Town Hall Yard"],
                        value=CollectorState.yard_id,
                        on_change=CollectorState.set_yard_id,
                        size="3", width="100%",
                    ),
                    rx.text("Тип мешка", weight="bold", size="2"),
                    rx.radio(
                        ["ORGANIC", "CLEAN_DRY", "DIRTY_MIXED"],
                        value=CollectorState.bag_type,
                        on_change=CollectorState.set_bag_type,
                        direction="column", spacing="2",
                    ),
                    rx.text("Транспорт", weight="bold", size="2"),
                    rx.select(
                        ["rickshaw", "truck", "walking"],
                        value=CollectorState.transport,
                        on_change=CollectorState.set_transport,
                        size="3", width="100%",
                    ),
                    rx.button(
                        "Зарегистрировать вывоз",
                        on_click=CollectorState.submit_collection,
                        loading=CollectorState.is_submitting,
                        color_scheme="jade", size="3", width="100%",
                    ),
                    rx.cond(CollectorState.message != "", rx.text(CollectorState.message, color="green")),
                    spacing="4", width="100%",
                ),
                max_width="500px", width="100%", margin_x="auto",
                padding={"initial": "4", "md": "6"},
            ),
            rx.link(rx.button("На главную", variant="soft", size="3"), href="/"),
            spacing={"initial": "4", "md": "5"}, width="100%", padding={"initial": "2", "md": "4"},
        ),
        max_width="1200px",
    )