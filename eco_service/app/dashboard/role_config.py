from typing import Dict, Any, List

ROLE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "COLLECTOR": {
        "title": "Портал сборщика",
        "subtitle": "Регистрация поступления и логистики отходов по площадкам (Yards)",
        "badge_color": "jade",
        "action_icon": "truck",
        "action_text": "Зарегистрировать вывоз мешка",
        "route": "/collector",
        "fields": [
            {
                "name": "yard_id",
                "label": "Площадка сбора (Yard)",
                "type": "select",
                "options": ["Central Yard", "Solar Kitchen Yard", "Town Hall Yard"],
                "placeholder": "Выберите площадки сбора..."
            },
            {
                "name": "bag_type",
                "label": "Тип поступающего мешка",
                "type": "radio",
                "options": ["ORGANIC", "CLEAN_DRY", "DIRTY_MIXED"],
                "default": "ORGANIC"
            },
            {
                "name": "logistics_type",
                "label": "Транспорт логистики",
                "type": "select",
                "options": ["rickshaw", "truck", "walking"],
                "placeholder": "Выберите транспорт..."
            }
        ]
    },
    "SORTER": {
        "title": "Портал сортировщика",
        "subtitle": "Фиксация массы, распределение по фракциям и контроль качества",
        "badge_color": "blue",
        "action_icon": "scale",
        "action_text": "Сохранить вес и сортировку",
        "route": "/sorter",
        "fields": [
            {
                "name": "bag_id",
                "label": "ID мешка / QR-код",
                "type": "input_text",
                "placeholder": "Отсканируйте или введите UUID мешка..."
            },
            {
                "name": "weight_kg",
                "label": "Точный вес мешка (кг)",
                "type": "input_number",
                "placeholder": "0.00"
            },
            {
                "name": "category_code",
                "label": "Категория фракции",
                "type": "select",
                "options": ["PLASTIC", "ORGANIC", "PAPER", "GLASS", "TEXTILE", "NON_RECYCLABLE_KITCHEN"],
                "placeholder": "Выберите категорию..."
            },
            {
                "name": "is_contaminated",
                "label": "Загрязнение / Замечания по качеству фракции",
                "type": "checkbox"
            }
        ]
    },
    "MANAGER": {
        "title": "Панель оперативного управления менеджера",
        "subtitle": "Мониторинг объема сбора, загрузки площадок и эффективности операторов",
        "badge_color": "amber",
        "action_icon": "refresh-cw",
        "action_text": "Обновить сводку данных",
        "route": "/manager",
        "fields": []
    }
}