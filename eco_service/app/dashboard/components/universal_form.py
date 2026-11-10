import reflex as rx
from app.dashboard.role_config import ROLE_CONFIGS

class UniversalFormState(rx.State):
    """Единый стейт для динамических полей."""
    form_data: dict = {}
    is_submitting: bool = False
    feedback_message: str = ""

    def set_field_value(self, key: str, value: Any):
        self.form_data[key] = value

    async def handle_submit(self, role: str):
        self.is_submitting = True
        # Универсальная логика отправки на бэкенд в зависимости от роли
        self.feedback_message = f"Данные для роли {role} успешно сохранены!"
        self.is_submitting = False


def render_field(field_def: dict) -> rx.Component:
    """Динамический генератор элементов управления."""
    f_type = field_def["type"]
    f_name = field_def["name"]
    f_label = field_def["label"]

    if f_type == "select":
        return rx.vstack(
            rx.text(f_label, weight="bold", size="2"),
            rx.select(
                field_def["options"],
                placeholder="Выберите...",
                on_change=lambda val: UniversalFormState.set_field_value(f_name, val),
                size="3",
                width="100%",
            ),
            width="100%", spacing="1",
        )
    elif f_type == "radio":
        return rx.vstack(
            rx.text(f_label, weight="bold", size="2"),
            rx.radio(
                field_def["options"],
                direction="row",
                spacing="4",
                on_change=lambda val: UniversalFormState.set_field_value(f_name, val),
            ),
            width="100%", spacing="1",
        )
    elif f_type == "input_text" or f_type == "input_number":
        return rx.vstack(
            rx.text(f_label, weight="bold", size="2"),
            rx.input(
                type="number" if f_type == "input_number" else "text",
                placeholder=field_def.get("placeholder", ""),
                on_change=lambda val: UniversalFormState.set_field_value(f_name, val),
                size="3",
                width="100%",
            ),
            width="100%", spacing="1",
        )
    elif f_type == "checkbox":
        return rx.hstack(
            rx.checkbox(
                on_change=lambda val: UniversalFormState.set_field_value(f_name, val),
            ),
            rx.text(f_label, size="2"),
            align="center", spacing="2",
        )
    return rx.fragment()


def universal_operator_card(user_role: str) -> rx.Component:
    """Карточка-контейнер, собирающая интерфейс под любую роль."""
    config = ROLE_CONFIGS.get(user_role, ROLE_CONFIGS["COLLECTOR"])

    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(config["title"], size="4"),
                rx.badge(user_role, color_scheme=config["badge_color"]),
                justify="between", align="center", width="100%",
            ),
            rx.text(config["subtitle"], size="2", color_scheme="gray"),
            rx.divider(),

            # Динамический рендер полей
            rx.foreach(config["fields"], render_field),

            # Кнопка отправки
            rx.button(
                rx.hstack(
                    rx.icon(config["action_icon"], size=18),
                    rx.text(config["action_text"]),
                ),
                on_click=lambda: UniversalFormState.handle_submit(user_role),
                loading=UniversalFormState.is_submitting,
                color_scheme="jade" if user_role == "COLLECTOR" else "blue",
                size="3",
                width="100%",
                margin_top="2",
            ),
            spacing="4", width="100%",
        ),
        size="3", width="100%",
    )