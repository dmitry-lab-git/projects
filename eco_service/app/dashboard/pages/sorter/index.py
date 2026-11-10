import reflex as rx

class SorterState(rx.State):
    bag_id: str = ""
    weight_kg: float = 0.0
    category_code: str = "PLASTIC"
    is_contaminated: bool = False
    is_submitting: bool = False
    message: str = ""

    # Explicit setters for sorter form fields
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
        # Database logic for logging weight and sorting results
        self.message = "Sorting results successfully saved!"
        self.is_submitting = False

@rx.page(route="/sorter", title="EcoService ERP | Sorter")
def sorter_page() -> rx.Component:
    return rx.container(
        # Основной вертикальный стек центрирует контент по двум осям на ПК
        rx.vstack(
            rx.heading("Sorter Portal (SORTER)", size={"initial": "5", "md": "7"}, width="100%"),
            rx.text("Weighing and fraction allocation", color_scheme="gray", size={"initial": "2", "md": "3"}, width="100%"),
            rx.divider(width="100%"),
            
            rx.card(
                rx.vstack(
                    rx.text("Bag ID / QR Code", weight="bold", size="2"),
                    rx.input(
                        placeholder="Enter bag UUID...",
                        value=SorterState.bag_id,
                        on_change=SorterState.set_bag_id,
                        size="3", width="100%",
                    ),
                    rx.text("Exact Weight (kg)", weight="bold", size="2"),
                    rx.input(
                        type="number",
                        placeholder="0.00",
                        value=SorterState.weight_kg.to_string(),
                        on_change=SorterState.set_weight_kg,
                        size="3", width="100%",
                    ),
                    rx.text("Fraction", weight="bold", size="2"),
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
                        rx.text("Contamination / Remarks", size="2"),
                        align="center", spacing="2",
                    ),
                    
                    # Основное действие формы
                    rx.button(
                        "Save Results",
                        on_click=SorterState.submit_sorting,
                        loading=SorterState.is_submitting,
                        color_scheme="blue", size="3", width="100%",
                    ),
                    rx.cond(SorterState.message != "", rx.text(SorterState.message, color="blue")),
                    
                    # Разделитель внутри карточки
                    rx.divider(margin_y="2"),
                    
                    # Навигационная кнопка во всю ширину
                    rx.link(
                        rx.button(
                            "Back to Home",
                            variant="soft",
                            size="3",
                            width="100%",
                        ),
                        href="/",
                        width="100%",
                    ),
                    spacing="4", width="100%",
                ),
                width="100%",
                padding={"initial": "4", "md": "6"},
            ),
            spacing={"initial": "4", "md": "5"}, 
            max_width="500px", 
            width="100%", 
            margin_x="auto", 
            justify="center",       # Центрирование содержимого по вертикали
            align_items="center",   # Центрирование содержимого по горизонтали
            min_height="90vh",      # Занимает почти всю высоту экрана для идеального фокуса по центру
            padding_y={"initial": "4", "md": "0"},
            padding_x={"initial": "2", "md": "4"},
        ),
        max_width="1200px",
    )
