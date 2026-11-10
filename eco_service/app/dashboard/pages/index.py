import reflex as rx

@rx.page(route="/", title="EcoService ERP | Home")
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            # Welcome Header Section
            rx.vstack(
                rx.heading("Auroville ERP System", size={"initial": "6", "md": "8"}),
                rx.text(
                    "Modular waste management and logistics platform for the field pilot project",
                    color_scheme="gray",
                    size={"initial": "3", "md": "4"},
                ),
                spacing="2",
                align="center",
                text_align="center",
                padding_y={"initial": "4", "md": "8"},
            ),
            
            rx.divider(),

            # Role-Based Quick Access Cards
            rx.grid(
                # Collector Access Card
                rx.card(
                    rx.vstack(
                        rx.icon("truck", size=32, color="var(--jade-9)"),
                        rx.heading("Collector", size="5"),
                        rx.text(
                            "Log waste collection from yards, select bag types, and manage transport details.",
                            size="2", color_scheme="gray",
                        ),
                        rx.spacer(),
                        rx.link(
                            rx.button("Open Portal", color_scheme="jade", size="3", width="100%"),
                            href="/collector",
                            width="100%",
                        ),
                        spacing="4", height="100%",
                    ),
                    size="3",
                ),
                
                # Sorter Access Card
                rx.card(
                    rx.vstack(
                        rx.icon("scale", size=32, color="var(--blue-9)"),
                        rx.heading("Sorter", size="5"),
                        rx.text(
                            "Weigh bags by ID, allocate materials into fractions, and monitor contamination levels.",
                            size="2", color_scheme="gray",
                        ),
                        rx.spacer(),
                        rx.link(
                            rx.button("Open Portal", color_scheme="blue", size="3", width="100%"),
                            href="/sorter",
                            width="100%",
                        ),
                        spacing="4", height="100%",
                    ),
                    size="3",
                ),
                
                # Manager / CEO Access Card
                rx.card(
                    rx.vstack(
                        rx.icon("layout-dashboard", size=32, color="var(--amber-9)"),
                        rx.heading("Manager / CEO", size="5"),
                        rx.text(
                            "Analytical dashboards, waste stream tracking, operational KPIs, and staff reports.",
                            size="2", color_scheme="gray",
                        ),
                        rx.spacer(),
                        rx.link(
                            rx.button("Open Dashboard", color_scheme="amber", size="3", width="100%"),
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

