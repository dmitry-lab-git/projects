import reflex as rx
from pwa.state.infrastructure import InfrastructureState


def infrastructure_form() -> rx.Component:
    return rx.vstack(
        # 1. Utilization Summary with month filter and tabs
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading("Utilization Summary", size="4"),
                    rx.spacer(),
                    rx.input(
                        type="month",
                        value=InfrastructureState.selected_month,
                        on_change=InfrastructureState.set_selected_month,
                        width="auto",
                    ),
                    width="100%",
                    align="center",
                ),
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("By Point", value="by_point"),
                        rx.tabs.trigger("By Resource", value="by_resource"),
                    ),
                    # Tab 1: Breakdown by disposal points
                    rx.tabs.content(
                        rx.cond(
                            InfrastructureState.monthly_summary.length() > 0,
                            rx.scroll_area(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Disposal Point"),
                                            rx.table.column_header_cell("Mass"),
                                            rx.table.column_header_cell("Count"),
                                        ),
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            InfrastructureState.monthly_summary,
                                            lambda row: rx.table.row(
                                                rx.table.cell(
                                                    row["disposition_point_name"], white_space="nowrap"
                                                ),
                                                rx.table.cell(
                                                    row["total_mass"], white_space="nowrap"
                                                ),
                                                rx.table.cell(
                                                    row["record_count"], white_space="nowrap"
                                                ),
                                            ),
                                        ),
                                    ),
                                    width="100%",
                                ),
                                width="100%",
                            ),
                            rx.text("No records found for the selected month.", color="gray", size="2"),
                        ),
                        value="by_point",
                    ),
                    # Tab 2: Breakdown by materials/resources
                    rx.tabs.content(
                        rx.cond(
                            InfrastructureState.resource_summary.length() > 0,
                            rx.scroll_area(
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Resource / Material"),
                                            rx.table.column_header_cell("Mass"),
                                            rx.table.column_header_cell("Count"),
                                        ),
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            InfrastructureState.resource_summary,
                                            lambda row: rx.table.row(
                                                rx.table.cell(
                                                    row["resource_name"], white_space="nowrap"
                                                ),
                                                rx.table.cell(
                                                    row["total_mass"], white_space="nowrap"
                                                ),
                                                rx.table.cell(
                                                    row["record_count"], white_space="nowrap"
                                                ),
                                            ),
                                        ),
                                    ),
                                    width="100%",
                                ),
                                width="100%",
                            ),
                            rx.text("No records found for the selected month.", color="gray", size="2"),
                        ),
                        value="by_resource",
                    ),
                    default_value="by_point",
                    width="100%",
                ),
                spacing="3",
            ),
            width="100%",
        ),
        # 2. Add Material
        rx.card(
            rx.vstack(
                rx.heading("Add Material", size="4"),
                rx.form.root(
                    rx.vstack(
                        rx.input(
                            placeholder="Material Name",
                            name="material_name",
                            required=True,
                        ),
                        rx.input(
                            placeholder="Resource Type", name="resource_type"
                        ),
                        rx.input(
                            placeholder="Unit of Measure", name="default_unit"
                        ),
                        rx.input(
                            placeholder="Container Type", name="container_type"
                        ),
                        rx.button("Save Resource", type="submit"),
                    ),
                    on_submit=InfrastructureState.add_resource,
                    reset_on_submit=True,
                ),
                spacing="3",
            ),
            width="100%",
        ),
        # 3. Log Consumption
        rx.card(
            rx.vstack(
                rx.heading("Log Consumption", size="4"),
                rx.form.root(
                    rx.vstack(
                        rx.select(
                            InfrastructureState.resource_names,
                            value=InfrastructureState.selected_resource_name,
                            on_change=InfrastructureState.set_selected_resource_name,
                            placeholder="Select resource...",
                            width="100%",
                        ),
                        rx.select(
                            InfrastructureState.device_names,
                            value=InfrastructureState.selected_device_name,
                            on_change=InfrastructureState.set_selected_device_name,
                            placeholder="Select device...",
                            width="100%",
                        ),
                        rx.select(
                            InfrastructureState.disposition_point_names,
                            value=InfrastructureState.selected_disposal_point_name,
                            on_change=InfrastructureState.set_selected_disposal_point_name,
                            placeholder="Select disposal point...",
                            width="100%",
                        ),
                        rx.select(
                            ["gross", "net"],
                            name="weighing_type",
                            default_value="gross",
                            placeholder="Weighing type...",
                            width="100%",
                        ),
                        rx.input(
                            placeholder="Quantity",
                            name="quantity",
                            type="number",
                            step="0.001",
                            required=True,
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.checkbox(
                                    checked=InfrastructureState.use_current_date,
                                    on_change=InfrastructureState.set_use_current_date,
                                ),
                                rx.text(
                                    "Use current date",
                                    size="2",
                                    white_space="nowrap",
                                ),
                                align="center",
                                spacing="2",
                            ),
                            rx.input(
                                name="utilized_at",
                                type="date",
                                disabled=InfrastructureState.use_current_date,
                                value=rx.cond(
                                    InfrastructureState.use_current_date,
                                    InfrastructureState.today_date_str,
                                    InfrastructureState.selected_date,
                                ),
                                on_change=InfrastructureState.set_selected_date,
                                width="100%",
                            ),
                            width="100%",
                            align="start",
                            spacing="2",
                        ),
                        rx.button("Log Consumption", type="submit"),
                    ),
                    on_submit=InfrastructureState.add_disposition,
                ),
                spacing="3",
            ),
            width="100%",
        ),
        rx.divider(margin_y="1em"),
        rx.heading("Latest 20 Transactions", size="4"),
        rx.scroll_area(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Date"),
                        rx.table.column_header_cell("Resource"),
                        rx.table.column_header_cell("Quantity"),
                        rx.table.column_header_cell("Device"),
                        rx.table.column_header_cell("Disposal Point"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        InfrastructureState.disposition_history,
                        lambda row: rx.table.row(
                            rx.table.cell(
                                row["created_at"], white_space="nowrap"
                            ),
                            rx.table.cell(
                                row["material_name"], white_space="nowrap"
                            ),
                            rx.table.cell(
                                row["quantity"], white_space="nowrap"
                            ),
                            rx.table.cell(
                                row["device_name"], white_space="nowrap"
                            ),
                            rx.table.cell(
                                row["disposition_point_name"],
                                white_space="nowrap",
                            ),
                        ),
                    ),
                ),
                width="100%",
            ),
            width="100%",
        ),
        spacing="4",
        width="100%",
    )