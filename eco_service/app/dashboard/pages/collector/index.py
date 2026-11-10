import reflex as rx

class CollectorState(rx.State):
    yard_id: str = "Central Yard"
    bag_type: str = "ORGANIC"
    transport: str = "rickshaw"
    is_submitting: bool = False
    message: str = ""

    def set_yard_id(self, value: str):
        self.yard_id = value

    def set_bag_type(self, value: str):
        self.bag_type = value

    def set_transport(self, value: str):
        self.transport = value

    async def submit_collection(self):
        self.is_submitting = True
        # Database logic for logging collection data
        self.message = "Collection successfully registered!"
        self.is_submitting = False

@rx.page(route="/collector", title="EcoService ERP | Collector")
def collector_page() -> rx.Component:
    return rx.container(
        # Основной вертикальный стек центрирует контент по двум осям на ПК
        rx.vstack(
            rx.heading("Collector Portal (COLLECTOR)", size={"initial": "5", "md": "7"}, width="100%"),
            rx.text("Log bag intake and arrivals from collection yards", color_scheme="gray", size={"initial": "2", "md": "3"}, width="100%"),
            rx.divider(width="100%"),
            
            rx.card(
                rx.vstack(
                    rx.text("Collection Yard", weight="bold", size="2"),
                    rx.select(
                        ["Central Yard", "Solar Kitchen Yard", "Town Hall Yard"],
                        value=CollectorState.yard_id,
                        on_change=CollectorState.set_yard_id,
                        size="3", width="100%",
                    ),
                    rx.text("Bag Type / Base Category", weight="bold", size="2"),
                    rx.select(
                        [
                            "ORGANIC", "PLASTIC", "PAPER", "CARDBOARD", "GLASS_UNBROKEN", 
                            "GLASS_BROKEN", "METAL", "TETRAPACK", "THERMOCOL", 
                            "SANITARY", "TEXTILE", "BATTERIES", "TYRES"
                        ],
                        value=CollectorState.bag_type,
                        on_change=CollectorState.set_bag_type,
                        size="3", width="100%",
                    ),
                    rx.text("Transport Type", weight="bold", size="2"),
                    rx.select(
                        ["rickshaw", "truck", "walking"],
                        value=CollectorState.transport,
                        on_change=CollectorState.set_transport,
                        size="3", width="100%",
                    ),
                    
                    # Основное действие формы
                    rx.button(
                        "Register Collection",
                        on_click=CollectorState.submit_collection,
                        loading=CollectorState.is_submitting,
                        color_scheme="jade", size="3", width="100%",
                    ),
                    rx.cond(CollectorState.message != "", rx.text(CollectorState.message, color="green")),
                    
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
