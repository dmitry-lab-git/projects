import reflex as rx

class SorterState(rx.State):
    bag_id: str = ""
    weight_kg: float = 0.0
    category_code: str = "PLASTIC"
    is_contaminated: bool = False
    is_submitting: bool = False
    message: str = ""

    # Явные сеттеры для полей формы сортировщика
    def set_bag_id(self, value: str):
        self.bag_id = value

    def set_weight_kg(self, value: str):
        try:
            self.weight_kg = float(value)
        except ValueError:
            self.weight_kg = 0.0

    def set_category_code(self, value: str):
        self.category_code = value

    def set_is_contaminated(self, value: bool):
        self.is_contaminated = value

    async def submit_sorting(self):
        self.is_submitting = True
        # Логика записи взвешивания и сортировки в БД
        self.message = "Результаты сортировки сохранены!"
        self.is_submitting = False

@rx.page(route="/sorter", title="EcoService ERP | Сортировщик")
def sorter_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("Портал сортировщика (SORTER)", size={"initial": "5", "md": "7"}),
            rx.text("Взвешивание и распределение по фракциям", color_scheme="gray", size={"initial": "2", "md": "3"}),
            rx.divider(),
            
            rx.card(
                rx.vstack(
                    rx.text("ID мешка / QR-код", weight="bold", size="2"),
                    rx.input(
                        placeholder="Введите UUID мешка...",
                        value=SorterState.bag_id,
                        on_change=SorterState.set_bag_id,
                        size="3", width="100%",
                    ),
                    rx.text("Точный вес (кг)", weight="bold", size="2"),
                    rx.input(
                        type="number",
                        placeholder="0.00",
                        value=SorterState.weight_kg.to_string(),
                        on_change=SorterState.set_weight_kg,
                        size="3", width="100%",
                    ),
                    rx.text("Фракция", weight="bold", size="2"),
                    rx.select(
                        ["PLASTIC", "ORGANIC", "PAPER", "GLASS", "TEXTILE", "NON_RECYCLABLE_KITCHEN"],
                        value=SorterState.category_code,
                        on_change=SorterState.set_category_code,
                        size="3", width="100%",
                    ),
                    rx.hstack(
                        rx.checkbox(
                            checked=SorterState.is_contaminated,
                            on_change=SorterState.set_is_contaminated,
                        ),
                        rx.text("Загрязнение / Замечания", size="2"),
                        align="center", spacing="2",
                    ),
                    rx.button(
                        "Сохранить результаты",
                        on_click=SorterState.submit_sorting,
                        loading=SorterState.is_submitting,
                        color_scheme="blue", size="3", width="100%",
                    ),
                    rx.cond(SorterState.message != "", rx.text(SorterState.message, color="blue")),
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