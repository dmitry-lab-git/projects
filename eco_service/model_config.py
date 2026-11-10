from datetime import datetime

# ============================================================================
# SIMULATION GLOBAL CONFIGURATION (Auroville 2-Month Pilot)
# ============================================================================

SIMULATION_START_DATE = datetime(2026, 9, 1, 7, 0, 0)
SIMULATION_END_DATE = datetime(2026, 10, 31, 21, 0, 0)

# Вероятность генерации мешка за сутки для рядового домохозяйства
# Скорректирована до 0.55 для корректного охвата распределения всех 12 фракций
HOUSEHOLD_DAILY_ACTIVITY_PROBABILITY = 0.55

# Роли операторов, задействованные в симуляции цепочки обработки отходов
SIMULATION_OPERATOR_ROLES = {
    "COLLECTOR": "COLLECTOR",
    "SORTER": "SORTER"
}

# ============================================================================
# HOUSEHOLD WASTE MODEL (Target: ~56.6 kg/month baseline)
# ============================================================================

# Профили отходов для рядовых домохозяйств (на основе базовых категорий Auroville Eco Service)
# Поле "weight" определяет математический вес (вероятность) выбора конкретной фракции
HOUSEHOLD_WASTE_PROFILE = {
    "ORGANIC": {
        "weight_range": (0.83, 1.17),        # Таргет: 25 - 35 кг/мес (вынос почти ежедневно)
        "category_code": "ORGANIC",
        "weight": 0.530
    },
    "NON_RECYCLABLE_KITCHEN": {
        "weight_range": (0.33, 0.53),        # Таргет: 5 - 8 кг/мес (вынос раз в 2-3 дня)
        "category_code": "NON_RECYCLABLE_KITCHEN",
        "weight": 0.115
    },
    "SANITARY": {
        "weight_range": (0.27, 0.47),        # Таргет: 4 - 7 кг/мес (вынос раз в 2-3 дня)
        "category_code": "SANITARY",
        "weight": 0.097
    },
    "PLASTIC": {
        "weight_range": (0.40, 0.60),        # Таргет: 4 - 6 кг/мес (1-2 раза в неделю)
        "category_code": "PLASTIC",
        "weight": 0.088
    },
    "CARDBOARD": {
        "weight_range": (0.45, 0.90),        # Таргет: часть от 3 - 6 кг/мес макулатуры
        "category_code": "CARDBOARD",
        "weight": 0.040
    },
    "PAPER": {
        "weight_range": (0.15, 0.35),        # Таргет: часть от 3 - 6 кг/мес макулатуры
        "category_code": "PAPER",
        "weight": 0.040
    },
    "GLASS_UNBROKEN": {
        "weight_range": (1.00, 2.50),        # Таргет: целое стекло (вынос раз в 2 недели)
        "category_code": "GLASS_UNBROKEN",
        "weight": 0.045
    },
    "GLASS_BROKEN": {
        "weight_range": (0.30, 0.80),        # Таргет: стеклобой (редко)
        "category_code": "GLASS_BROKEN",
        "weight": 0.010
    },
    "TETRAPACK": {
        "weight_range": (0.22, 0.43),        # Таргет: 1.5 - 3 кг/мес (вынос раз в неделю)
        "category_code": "TETRAPACK",
        "weight": 0.020
    },
    "METAL": {
        "weight_range": (0.20, 0.40),        # Таргет: 1 - 2 кг/мес (консервные банки)
        "category_code": "METAL",
        "weight": 0.012
    },
    "THERMOCOL": {
        "weight_range": (0.15, 0.50),        # Таргет: 0 - 1 кг/мес (экстремально редкий)
        "weight": 0.002,
        "category_code": "THERMOCOL"
    },
    "TEXTILE": {
        "weight_range": (0.50, 1.50),        # Таргет: 0.5 - 2 кг/мес (раз в сезон)
        "category_code": "TEXTILE",
        "weight": 0.001
    }
}

# ============================================================================
# ORGANIZATION WASTE PROFILES (Strictly aligned with Auroville Ecosystem)
# ============================================================================

ORGANIZATION_WASTE_PROFILES = {
    # 1. Рестораны / Общепит (Пример: Auroville Bakery)
    "RESTAURANT": [
        {
            "bag_type_code": "ORGANIC",
            "category_code": "ORGANIC",
            "weight_range": (7.0, 18.0),       # Суммарно 200 - 500 кг/мес (вынос ежедневно)
            "daily_probability": 0.95
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "CARDBOARD",
            "weight_range": (3.5, 7.0),        # Крупные коробки и мешки от сырья
            "daily_probability": 0.40
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PAPER",
            "weight_range": (1.0, 3.0),
            "daily_probability": 0.40
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PLASTIC",
            "weight_range": (2.0, 4.5),        # Стретч-пленка, ПЭТ-тара, канистры
            "daily_probability": 0.45
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "NON_RECYCLABLE_KITCHEN", # Жирный кухонный пластик, салфетки
            "weight_range": (0.7, 1.6),
            "daily_probability": 0.90
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "GLASS_UNBROKEN",
            "weight_range": (1.5, 4.5),        # Банки от соусов, конфитюров
            "daily_probability": 0.15
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "GLASS_BROKEN",
            "weight_range": (0.5, 2.0),        # Разбитая посуда и стеклобой
            "daily_probability": 0.10
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "METAL",            # Жестяная тара от масла и пюре
            "weight_range": (0.5, 1.5),
            "daily_probability": 0.20
        }
    ],
    
    # 2. Офисы и распределительные центры (Пример: PTDC, Visitors Centre Shop, Computation Group)
    "OFFICE": [
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "CARDBOARD",      # Упаковочные коробки дистрибьюторов (PTDC)
            "weight_range": (3.0, 8.0),
            "daily_probability": 0.25
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PAPER",          # Офисный бумажный документооборот
            "weight_range": (1.5, 4.5),
            "daily_probability": 0.30
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PLASTIC",        # ПЭТ, бутылки из-под воды, обеды
            "weight_range": (0.7, 2.0),
            "daily_probability": 0.30
        },
        {
            "bag_type_code": "ORGANIC",
            "category_code": "ORGANIC",          # Кофейный жмых, остатки из офисной кухни
            "weight_range": (0.3, 0.6),
            "daily_probability": 0.75
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "SANITARY",        # Одноразовые полотенца из санузлов
            "weight_range": (0.3, 0.7),
            "daily_probability": 0.50
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "BATTERIES",       # Электронные компоненты и батарейки (Computation Group)
            "weight_range": (0.1, 0.5),
            "daily_probability": 0.02
        }
    ],
    
    # 3. Производства и мастерские (Пример: Auroville Press, La Ferme Woodworks)
    "FACTORY": [
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PAPER",          # Тонны бумажных обрезков Auroville Press
            "weight_range": (15.0, 35.0),
            "daily_probability": 0.45
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "CARDBOARD",
            "weight_range": (5.0, 15.0),
            "daily_probability": 0.40
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "METAL",            # Металлические элементы, крепеж, диски Woodworks
            "weight_range": (10.0, 30.0),
            "daily_probability": 0.04
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PLASTIC",        # Тара и канистры от лаков, красок и клеев
            "weight_range": (1.5, 4.0),
            "daily_probability": 0.30
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "NON_RECYCLABLE_KITCHEN", # Производственный мусор: наждачка, ветошь
            "weight_range": (1.5, 3.5),
            "daily_probability": 0.35
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "TYRES",            # Станковые или грузовые покрышки
            "weight_range": (20.0, 40.0),
            "daily_probability": 0.01
        }
    ],
    
    # 4. Гостевые дома / Эко-лоджи (Пример: Sadhana Forest, Quiet Healing Center)
    "GUEST_HOUSE": [
        {
            "bag_type_code": "ORGANIC",
            "category_code": "ORGANIC",          # Гостевые кухни (привязаны к турсезону)
            "weight_range": (3.0, 8.0),
            "daily_probability": 0.85
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PLASTIC",        # Косметика, бытовая химия, ПЭТ
            "weight_range": (1.5, 4.0),
            "daily_probability": 0.45
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "SANITARY",        # Гигиена из номеров и процедурных комнат
            "weight_range": (1.5, 3.5),
            "daily_probability": 0.50
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PAPER",
            "weight_range": (0.8, 2.5),
            "daily_probability": 0.30
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "GLASS_UNBROKEN",  # Бутылки от напитков и масел Quiet Center
            "weight_range": (2.0, 6.0),
            "daily_probability": 0.15
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "TEXTILE",         # Изношенное постельное белье и полотенца
            "weight_range": (3.0, 10.0),
            "daily_probability": 0.04
        }
    ],
    
    # 5. Специфические объекты (Пример: Isai Ambalam School, Botanical Garden)
    "OTHER": [
        {
            "bag_type_code": "ORGANIC",
            "category_code": "ORGANIC",          # Столовая школы + зеленый мусор ботанического сада
            "weight_range": (2.5, 6.5),
            "daily_probability": 0.60
            },
            {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PLASTIC",        # Садовые горшки для рассады, инвентарь
            "weight_range": (1.5, 4.5),
            "daily_probability": 0.30
            },
            {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PAPER",          # Школьные тетради, учебные материалы, альбомы
            "weight_range": (1.5, 4.0),
            "daily_probability": 0.35
            },
            {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "SANITARY",        # Гигиеническое обеспечение детского потока
            "weight_range": (1.0, 2.5),
            "daily_probability": 0.45
            },
            {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "THERMOCOL",       # Пенопласт от макетов для школьных проектов
            "weight_range": (0.3, 1.2),
            "daily_probability": 0.05
            }
            ]
            }