import reflex as rx
from typing import Dict, Any, List


class OperatorFormState(rx.State):
    """Стейт для управления формой ввода данных оператора."""
    
    # Поля формы сборщика (COLLECTOR)
    selected_resident_id: str = ""
    selected_yard_id: str = ""
    selected_bag_type: str = "ORGANIC"
    logistics_transport: str = "rickshaw"
    
    # Поля формы сортировщика (SORTER)
    scanned_bag_id: str = ""
    weight_kg: float = 0.0
    selected_category: str = "PLASTIC"
    is_contaminated: bool = False
    
    # Статус отправки
    is_submitting: bool = False
    feedback_message: str = ""
    feedback_color: str = "green"

    def set_bag_type(self, value: str):
        self.selected_bag_type = value

    def set_category(self, value: str):
        self.selected_category = value

    async def submit_collection_event(self):
        """Отправка события приемки сборщиком."""
        if not self.selected_yard_id:
            self.feedback_message = "Пожалуйста, выберите площадку сбора (Yard)!"
            self.feedback_color = "red"
            return
            
        self.is_submitting = True
        self.feedback_message = ""
        
        # Здесь подключается логика вызова базы через asyncpg / backend service
        # Пример: await save_collection_bag(...)
        
        self.feedback_message = "Мешок успешно зарегистрирован и принят!"
        self.feedback_color = "green"
        self.is_submitting = False

    async def submit_sorting_event(self):
        """Отправка события взвешивания и сортировки."""
        if self.weight_kg <= 0:
            self.feedback_message = "Укажите корректный вес мешка!"
            self.feedback_color = "red"
            return
            
        self.is_submitting = True
        self.feedback_message = ""
        
        # Логика записи взвешивания и сортировки в infrastructure.bag_events
        
        self.feedback_message = "Результаты сортировки сохранены!"
        self.feedback_color = "green"
        self.is_submitting = False


def collector_form_fields() -> rx.Component:
    """Поля ввода для роли COLLECTOR (Сборщик)."""
    return rx.vstack(
        rx.vstack(
            rx.text("Площадка сбора (Yard)", weight="bold", size="2"),
            rx.select(
                ["Central Yard", "Solar Kitchen Yard", "Town Hall Yard"],
                placeholder="Выберите площадку...",
                on_change=OperatorFormState.set_selected_yard_id,
                size="3",
                width="100%",
            ),
            width="100%",
            spacing="1",
        ),
        rx.vstack(
            rx.text("Тип поступающего мешка", weight="bold", size="2"),
            rx.radio(
                ["ORGANIC", "CLEAN_DRY", "DIRTY_MIXED"],
                value=OperatorFormState.selected_bag_type,
                on_change=OperatorFormState.set_bag_type,
                direction="row",
                spacing="4",
            ),
            width="100%",
            spacing="1",
        ),
        rx.vstack(
            rx.text("Транспорт логистики", weight="bold", size="2"),
            rx.select(
                ["rickshaw", "truck", "walking"],
                value=OperatorFormState.logistics_transport,
                on_change=OperatorFormState.set_logistics_transport,
                size="3",
                width="100%",
            ),
            width="100%",
            spacing="1",
        ),
        rx.button(
            rx.hstack(
                rx.icon("truck", size=18),
                rx.text("Зарегистрировать вывоз"),
            ),
            on_click=OperatorFormState.submit_collection_event,
            loading=OperatorFormState.is_submitting,
            color_scheme="jade",
            size="3",
            width="100%",
            margin_top="2",
        ),
        spacing="4",
        width="100%",
    )


def sorter_form_fields() -> rx.Component:
    """Поля ввода для роли SORTER (Сортировщик)."""
    return rx.vstack(
        rx.vstack(
            rx.text("ID мешка / QR-код", weight="bold", size="2"),
            rx.input(
                placeholder="Введите или отсканируйте UUID...",
                value=OperatorFormState.scanned_bag_id,
                on_change=OperatorFormState.set_scanned_bag_id,
                size="3",
                width="100%",
            ),
            width="100%",
            spacing="1",
        ),
        rx.vstack(
            rx.text("Точный вес (кг)", weight="bold", size="2"),
            rx.input(
                type="number",
                placeholder="0.00",
                value=OperatorFormState.weight_kg.to_string(),
                on_change=OperatorFormState.set_weight_kg,
                size="3",
                width="100%",
            ),
            width="100%",
            spacing="1",
        ),
        rx.vstack(
            rx.text("Категория фракции", weight="bold", size="2"),
            rx.select(
                ["PLASTIC", "ORGANIC", "PAPER", "GLASS", "TEXTILE", "NON_RECYCLABLE_KITCHEN"],
                value=OperatorFormState.selected_category,
                on_change=OperatorFormState.set_category,
                size="3",
                width="100%",
            ),
            width="100%",
            spacing="1",
        ),
        rx.hstack(
            rx.checkbox(
                checked=OperatorFormState.is_contaminated,
                on_change=OperatorFormState.set_is_contaminated,
            ),
            rx.text("Загрязнение / Замечания по фракции", size="2"),
            align="center",
            spacing="2",
        ),
        rx.button(
            rx.hstack(
                rx.icon("scale", size=18),
                rx.text("Сохранить вес и сортировку"),
            ),
            on_click=OperatorFormState.submit_sorting_event,
            loading=OperatorFormState.is_submitting,
            color_scheme="blue",
            size="3",
            width="100%",
            margin_top="2",
        ),
        spacing="4",
        width="100%",
    )


def operator_action_card(user_role: str = "COLLECTOR") -> rx.Component:
    """Основной виджет формы оператора с переключением режима."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Ввод операционных данных", size="4"),
                rx.badge(
                    user_role,
                    color_scheme="jade" if user_role == "COLLECTOR" else "blue",
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.divider(),
            
            # Сообщение обратной связи
            rx.cond(
                OperatorFormState.feedback_message != "",
                rx.callout.root(
                    rx.callout.text(OperatorFormState.feedback_message),
                    color_scheme=OperatorFormState.feedback_color,
                    role="alert",
                    width="100%",
                ),
            ),
            
            # Динамический выбор формы по роли оператора
            rx.cond(
                user_role == "COLLECTOR",
                collector_form_fields(),
                sorter_form_fields(),
            ),
            
            spacing="4",
            width="100%",
        ),
        size="3",
        width="100%",
    )