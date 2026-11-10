from datetime import datetime

# ============================================================================
# SIMULATION GLOBAL CONFIGURATION (Auroville 2-Month Pilot)
# ============================================================================

SIMULATION_START_DATE = datetime(2026, 9, 1, 7, 0, 0)
SIMULATION_END_DATE = datetime(2026, 10, 31, 21, 0, 0)

# Вероятность генерации мешка за сутки для рядового домохозяйства
HOUSEHOLD_DAILY_ACTIVITY_PROBABILITY = 0.4

# Роли операторов, задействованные в симуляции цепочки обработки отходов
SIMULATION_OPERATOR_ROLES = {
    "COLLECTOR": "COLLECTOR",
    "SORTER": "SORTER"
}

# Профили отходов для рядовых домохозяйств
HOUSEHOLD_WASTE_PROFILE = {
    "ORGANIC": {
        "weight_range": (2.5, 3.2),
        "category_code": "ORGANIC",
        "weight": 0.5
    },
    "DIRTY_MIXED": {
        "weight_range": (0.25, 0.35),
        "category_code": "NON_RECYCLABLE_KITCHEN",
        "weight": 0.2
    },
    "CLEAN_DRY": {
        "weight_range": (0.2, 0.9),
        "category_code": "PLASTIC",
        "weight": 0.3
    }
}

# ============================================================================
# ORGANIZATION WASTE PROFILES (Strictly aligned with specification)
# ============================================================================

ORGANIZATION_WASTE_PROFILES = {
    "RESTAURANT": [
        {
            "bag_type_code": "ORGANIC",
            "category_code": "ORGANIC",
            "weight_range": (10.0, 14.0),
            "daily_probability": 0.95
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PLASTIC",
            "weight_range": (4.0, 6.0),
            "daily_probability": 0.35
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "NON_RECYCLABLE_KITCHEN",
            "weight_range": (8.0, 12.0),
            "daily_probability": 0.25
        }
    ],
    "OFFICE": [
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PAPER",
            "weight_range": (3.5, 4.5),
            "daily_probability": 0.35
        },
        {
            "bag_type_code": "ORGANIC",
            "category_code": "ORGANIC",
            "weight_range": (7.0, 9.0),
            "daily_probability": 0.2
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "NON_RECYCLABLE_KITCHEN",
            "weight_range": (6.0, 8.0),
            "daily_probability": 0.15
        }
    ],
    "FACTORY": [
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PAPER",
            "weight_range": (7.0, 9.0),
            "daily_probability": 0.55
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "TEXTILE",
            "weight_range": (8.0, 10.0),
            "daily_probability": 0.15
        },
        {
            "bag_type_code": "ORGANIC",
            "category_code": "ORGANIC",
            "weight_range": (7.0, 9.0),
            "daily_probability": 0.15
        }
    ],
    "GUEST_HOUSE": [
        {
            "bag_type_code": "ORGANIC",
            "category_code": "ORGANIC",
            "weight_range": (9.0, 11.0),
            "daily_probability": 0.75
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "GLASS",
            "weight_range": (3.5, 4.5),
            "daily_probability": 0.35
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "NON_RECYCLABLE_KITCHEN",
            "weight_range": (7.0, 9.0),
            "daily_probability": 0.15
        }
    ],
    "OTHER": [
        {
            "bag_type_code": "ORGANIC",
            "category_code": "ORGANIC",
            "weight_range": (8.0, 10.0),
            "daily_probability": 0.35
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PLASTIC",
            "weight_range": (4.0, 6.0),
            "daily_probability": 0.25
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "NON_RECYCLABLE_KITCHEN",
            "weight_range": (6.0, 8.0),
            "daily_probability": 0.15
        }
    ]
}