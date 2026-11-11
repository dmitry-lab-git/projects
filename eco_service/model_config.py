from datetime import datetime

# ============================================================================
# SIMULATION GLOBAL CONFIGURATION (Auroville 2-Month Pilot)
# ============================================================================

SIMULATION_START_DATE = datetime(2026, 9, 1, 7, 0, 0)
SIMULATION_END_DATE = datetime(2026, 10, 31, 21, 0, 0)

# Daily waste bag generation probability for a regular household
# Adjusted to 0.55 for accurate distribution coverage of all 12 fractions
HOUSEHOLD_DAILY_ACTIVITY_PROBABILITY = 0.55

# Operator roles involved in simulating the waste processing lifecycle
SIMULATION_OPERATOR_ROLES = {
    "COLLECTOR": "COLLECTOR",
    "SORTER": "SORTER"
}

# ============================================================================
# HOUSEHOLD WASTE MODEL (Target: ~56.6 kg/month baseline)
# ============================================================================

# Waste profiles for regular households (based on Auroville Eco Service baseline categories)
# The "weight" field determines the mathematical probability of selecting a specific fraction
HOUSEHOLD_WASTE_PROFILE = {
    "ORGANIC": {
        "weight_range": (0.83, 1.17),        # Target: 25 - 35 kg/month (almost daily disposal)
        "category_code": "ORGANIC",
        "weight": 0.530
    },
    "NON_RECYCLABLE_KITCHEN": {
        "weight_range": (0.33, 0.53),        # Target: 5 - 8 kg/month (disposal every 2-3 days)
        "category_code": "NON_RECYCLABLE_KITCHEN",
        "weight": 0.115
    },
    "SANITARY": {
        "weight_range": (0.27, 0.47),        # Target: 4 - 7 kg/month (disposal every 2-3 days)
        "category_code": "SANITARY",
        "weight": 0.097
    },
    "PLASTIC": {
        "weight_range": (0.40, 0.60),        # Target: 4 - 6 kg/month (1-2 times a week)
        "category_code": "PLASTIC",
        "weight": 0.088
    },
    "CARDBOARD": {
        "weight_range": (0.45, 0.90),        # Target: part of 3 - 6 kg/month waste paper
        "category_code": "CARDBOARD",
        "weight": 0.040
    },
    "PAPER": {
        "weight_range": (0.15, 0.35),        # Target: part of 3 - 6 kg/month waste paper
        "category_code": "PAPER",
        "weight": 0.040
    },
    "GLASS_UNBROKEN": {
        "weight_range": (1.00, 2.50),        # Target: unbroken glass (disposal every 2 weeks)
        "category_code": "GLASS_UNBROKEN",
        "weight": 0.045
    },
    "GLASS_BROKEN": {
        "weight_range": (0.30, 0.80),        # Target: broken glass (rarely)
        "category_code": "GLASS_BROKEN",
        "weight": 0.010
    },
    "TETRAPACK": {
        "weight_range": (0.22, 0.43),        # Target: 1.5 - 3 kg/month (disposal once a week)
        "category_code": "TETRAPACK",
        "weight": 0.020
    },
    "METAL": {
        "weight_range": (0.20, 0.40),        # Target: 1 - 2 kg/month (tin cans)
        "category_code": "METAL",
        "weight": 0.012
    },
    "THERMOCOL": {
        "weight_range": (0.15, 0.50),        # Target: 0 - 1 kg/month (extremely rare)
        "weight": 0.002,
        "category_code": "THERMOCOL"
    },
    "TEXTILE": {
        "weight_range": (0.50, 1.50),        # Target: 0.5 - 2 kg/month (once a season)
        "category_code": "TEXTILE",
        "weight": 0.001
    }
}

# ============================================================================
# ORGANIZATION WASTE PROFILES (Strictly aligned with Auroville Ecosystem)
# ============================================================================

ORGANIZATION_WASTE_PROFILES = {
    # 1. Restaurants / Food Service (Example: Auroville Bakery)
    "RESTAURANT": [
        {
            "bag_type_code": "ORGANIC",
            "category_code": "ORGANIC",
            "weight_range": (7.0, 18.0),       # Total 200 - 500 kg/month (daily disposal)
            "daily_probability": 0.95
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "CARDBOARD",      # Large boxes and bags from raw materials
            "weight_range": (3.5, 7.0),
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
            "category_code": "PLASTIC",        # Stretch wrap, PET containers, jerrycans
            "weight_range": (2.0, 4.5),
            "daily_probability": 0.45
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "NON_RECYCLABLE_KITCHEN", # Greasy kitchen plastic, napkins
            "weight_range": (0.7, 1.6),
            "daily_probability": 0.90
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "GLASS_UNBROKEN", # Sauce and jam jars
            "weight_range": (1.5, 4.5),
            "daily_probability": 0.15
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "GLASS_BROKEN",   # Broken tableware and glass fragments
            "weight_range": (0.5, 2.0),
            "daily_probability": 0.10
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "METAL",          # Metal containers from oil and puree
            "weight_range": (0.5, 1.5),
            "daily_probability": 0.20
        }
    ],
    
    # 2. Offices and Distribution Centers (Example: PTDC, Visitors Centre Shop, Computation Group)
    "OFFICE": [
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "CARDBOARD",      # Distributor packing boxes (PTDC)
            "weight_range": (3.0, 8.0),
            "daily_probability": 0.25
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PAPER",          # Office paper workflow
            "weight_range": (1.5, 4.5),
            "daily_probability": 0.30
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PLASTIC",        # PET water bottles, lunch boxes
            "weight_range": (0.7, 2.0),
            "daily_probability": 0.30
        },
        {
            "bag_type_code": "ORGANIC",
            "category_code": "ORGANIC",        # Coffee grounds, food scraps from office kitchen
            "weight_range": (0.3, 0.6),
            "daily_probability": 0.75
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "SANITARY",       # Disposable towels from restrooms
            "weight_range": (0.3, 0.7),
            "daily_probability": 0.50
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "BATTERIES",      # Electronic components and batteries (Computation Group)
            "weight_range": (0.1, 0.5),
            "daily_probability": 0.02
        }
    ],
    
    # 3. Production Facilities and Workshops (Example: Auroville Press, La Ferme Woodworks)
    "FACTORY": [
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PAPER",          # Tons of paper scraps from Auroville Press
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
            "category_code": "METAL",          # Metal elements, fasteners, blades from Woodworks
            "weight_range": (10.0, 30.0),
            "daily_probability": 0.04
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PLASTIC",        # Containers and jerrycans from varnishes, paints, glues
            "weight_range": (1.5, 4.0),
            "daily_probability": 0.30
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "NON_RECYCLABLE_KITCHEN", # Industrial waste: sandpaper, rags
            "weight_range": (1.5, 3.5),
            "daily_probability": 0.35
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "TYRES",          # Machine or truck tires
            "weight_range": (20.0, 40.0),
            "daily_probability": 0.01
        }
    ],
    
    # 4. Guesthouses / Eco-Lodges (Example: Sadhana Forest, Quiet Healing Center)
    "GUEST_HOUSE": [
        {
            "bag_type_code": "ORGANIC",
            "category_code": "ORGANIC",        # Guest kitchens (tied to tourist season)
            "weight_range": (3.0, 8.0),
            "daily_probability": 0.85
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PLASTIC",        # Cosmetics, household chemicals, PET
            "weight_range": (1.5, 4.0),
            "daily_probability": 0.45
        },
        {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "SANITARY",       # Hygiene waste from rooms and treatment facilities
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
            "category_code": "GLASS_UNBROKEN", # Beverage and oil bottles from Quiet Center
            "weight_range": (2.0, 6.0),
            "daily_probability": 0.15
        },
        {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "TEXTILE",        # Worn bed linen and towels
            "weight_range": (3.0, 10.0),
            "daily_probability": 0.04
        }
    ],
    
    # 5. Specific Facilities (Example: Isai Ambalam School, Botanical Garden)
    "OTHER": [
        {
            "bag_type_code": "ORGANIC",
            "category_code": "ORGANIC",        # School canteen + botanical garden green waste
            "weight_range": (2.5, 6.5),
            "daily_probability": 0.60
            },
            {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PLASTIC",        # Garden seedling pots, inventory
            "weight_range": (1.5, 4.5),
            "daily_probability": 0.30
            },
            {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "PAPER",          # School notebooks, study materials, art books
            "weight_range": (1.5, 4.0),
            "daily_probability": 0.35
            },
            {
            "bag_type_code": "DIRTY_MIXED",
            "category_code": "SANITARY",       # Hygiene support for student influx
            "weight_range": (1.0, 2.5),
            "daily_probability": 0.45
            },
            {
            "bag_type_code": "CLEAN_DRY",
            "category_code": "THERMOCOL",      # Styrofoam from mockups for school projects
            "weight_range": (0.3, 1.2),
            "daily_probability": 0.05
            }
            ]
            }