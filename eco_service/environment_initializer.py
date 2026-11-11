import asyncio
import json
import random
from datetime import timedelta
import uuid
from database import create_database_pool
from model_config import (
    SIMULATION_START_DATE, 
    SIMULATION_END_DATE, 
    HOUSEHOLD_DAILY_ACTIVITY_PROBABILITY,
    HOUSEHOLD_WASTE_PROFILE,
    ORGANIZATION_WASTE_PROFILES,
    SIMULATION_OPERATOR_ROLES
)

# Fixed UUIDs for system events in the bag lifecycle
EVENT_TYPES_MAP = {
    "SUBMITTED": uuid.UUID("fa4e5b22-8356-42d4-bb9e-4e4bf7e9b0e1"),
    "ARRIVED": uuid.UUID("3c2b81fa-9d1a-4d24-82a1-5fe11c784ab2"),
    "WEIGHED": uuid.UUID("9f8e7d6c-5b4a-4321-bd23-1a2b3c4d5e6f"),
    "SORTED": uuid.UUID("da2a13f5-62bb-4c22-b5e1-8f4b7a2c3d10")
}

# Mapping detailed household fractions to database bag types (fallback protection)
HOUSEHOLD_BAG_TYPE_FALLBACK = {
    "ORGANIC": "ORGANIC",
    "NON_RECYCLABLE_KITCHEN": "DIRTY_MIXED",
    "SANITARY": "DIRTY_MIXED",
    "PLASTIC": "CLEAN_DRY",
    "CARDBOARD": "CLEAN_DRY",
    "PAPER": "CLEAN_DRY",
    "GLASS_UNBROKEN": "CLEAN_DRY",
    "GLASS_BROKEN": "CLEAN_DRY",
    "TETRAPACK": "CLEAN_DRY",
    "METAL": "CLEAN_DRY",
    "THERMOCOL": "CLEAN_DRY",
    "TEXTILE": "CLEAN_DRY"
}

async def run_global_initialization():
    print("Opening connection pool for streamlined simulation...", flush=True)
    pool = await create_database_pool()
    
    async with pool.acquire() as conn:
        # 1. Truncate only transactional tables before starting simulation
        print("🔥 [1/3] Truncating transaction logs (bags & events)...", flush=True)
        await conn.execute("TRUNCATE TABLE infrastructure.bag_events CASCADE;")
        await conn.execute("TRUNCATE TABLE infrastructure.bags CASCADE;")

        # 2. Fetch necessary entities from database references
        print("📥 [2/3] Fetching reference entities from database...", flush=True)
        
        yards_db = await conn.fetch("SELECT yard_id FROM dicts.yards WHERE is_active = TRUE;")
        yard_ids = [row["yard_id"] for row in yards_db]
        if not yard_ids:
            raise ValueError("Error: dicts.yards is empty! Please seed yards before running simulation.")
        
        households_db = await conn.fetch("SELECT user_id AS resident_id, yard_id FROM dicts.households;")
        organizations_db = await conn.fetch("SELECT organization_id, business_type FROM dicts.organizations WHERE is_active = TRUE;")
        
        bag_types_db = await conn.fetch("SELECT type_id, code FROM dicts.bag_types;")
        bag_type_map = {row["code"]: row["type_id"] for row in bag_types_db}

        operators_db = await conn.fetch("SELECT operator_id, role FROM dicts.operators WHERE is_active = TRUE;")
        collector_uuids = [op["operator_id"] for op in operators_db if op["role"] == SIMULATION_OPERATOR_ROLES["COLLECTOR"]]
        sorter_uuids = [op["operator_id"] for op in operators_db if op["role"] == SIMULATION_OPERATOR_ROLES["SORTER"]]

        if not collector_uuids:
            collector_uuids = [uuid.uuid4()]
        if not sorter_uuids:
            sorter_uuids = [uuid.uuid4()]

        # 3. Timeline-based simulation launch
        print("🌊 [3/3] Replaying timeline based on model_config parameters...", flush=True)
        current_day = SIMULATION_START_DATE
        total_bags = 0

        while current_day <= SIMULATION_END_DATE:
            print(f"⏳ Simulating date: {current_day.strftime('%Y-%m-%d')} (Total bags so far: {total_bags})", flush=True)
            
            async with conn.transaction():
                # --- A. Household Generation ---
                for hh in households_db:
                    if random.random() < HOUSEHOLD_DAILY_ACTIVITY_PROBABILITY:
                        waste_types = list(HOUSEHOLD_WASTE_PROFILE.keys())
                        weights = [HOUSEHOLD_WASTE_PROFILE[wt]["weight"] for wt in waste_types]
                        chosen_wt = random.choices(waste_types, weights=weights)[0]
                        
                        profile = HOUSEHOLD_WASTE_PROFILE[chosen_wt]
                        
                        b_type_code = chosen_wt if chosen_wt in bag_type_map else HOUSEHOLD_BAG_TYPE_FALLBACK.get(chosen_wt)
                        b_type_uid = bag_type_map.get(b_type_code)
                        
                        if not b_type_uid:
                            b_type_uid = list(bag_type_map.values())[0] if bag_type_map else None
                            if not b_type_uid:
                                continue

                        total_bags += 1
                        bag_id = uuid.uuid4()
                        t_sub = current_day + timedelta(minutes=random.randint(60, 800))
                        weight = round(random.uniform(*profile["weight_range"]), 3)

                        current_collector = random.choice(collector_uuids)
                        current_sorter = random.choice(sorter_uuids)

                        await conn.execute(
                            "INSERT INTO infrastructure.bags (bag_id, resident_id, yard_id, type_id, created_at) VALUES ($1, $2, $3, $4, $5);",
                            bag_id, hh["resident_id"], hh["yard_id"], b_type_uid, t_sub
                        )
                        
                        events = [
                            (EVENT_TYPES_MAP["SUBMITTED"], None, t_sub, '{"source":"household_pwa"}'),
                            (EVENT_TYPES_MAP["ARRIVED"], current_collector, t_sub + timedelta(minutes=120), '{"logistics":"rickshaw"}'),
                            (EVENT_TYPES_MAP["WEIGHED"], current_sorter, t_sub + timedelta(minutes=135), json.dumps({"weight_kg": weight})),
                            (EVENT_TYPES_MAP["SORTED"], current_sorter, t_sub + timedelta(minutes=150), json.dumps({"is_contaminated": False, "allocations": [{"category_code": profile["category_code"], "weight_kg": weight}]}))
                        ]
                        
                        for ev_type_id, op_id, ev_time, payload in events:
                            await conn.execute(
                                "INSERT INTO infrastructure.bag_events (bag_id, event_type_id, operator_id, payload, occurred_at) VALUES ($1, $2, $3, $4::jsonb, $5);",
                                bag_id, ev_type_id, op_id, payload, ev_time
                            )

                # --- B. Organization Generation ---
                for org in organizations_db:
                    b_type_code = org["business_type"]
                    waste_streams = ORGANIZATION_WASTE_PROFILES.get(b_type_code, ORGANIZATION_WASTE_PROFILES["OTHER"])
                    
                    for stream in waste_streams:
                        if random.random() < stream["daily_probability"]:
                            b_type_uid = bag_type_map.get(stream["bag_type_code"], bag_type_map.get("CLEAN_DRY"))
                            if not b_type_uid and bag_type_map:
                                b_type_uid = list(bag_type_map.values())[0]
                            if not b_type_uid:
                                continue

                            total_bags += 1
                            bag_id = uuid.uuid4()
                            t_sub = current_day + timedelta(hours=random.randint(8, 16))
                            random_yard_id = random.choice(yard_ids)
                            weight = round(random.uniform(*stream["weight_range"]), 3)
                            
                            org_resident_id = households_db[0]["resident_id"] if households_db else uuid.uuid4()

                            current_collector = random.choice(collector_uuids)
                            current_sorter = random.choice(sorter_uuids)

                            await conn.execute(
                                "INSERT INTO infrastructure.bags (bag_id, resident_id, yard_id, type_id, created_at) VALUES ($1, $2, $3, $4, $5);",
                                bag_id, org_resident_id, random_yard_id, b_type_uid, t_sub
                            )
                            
                            events = [
                                (EVENT_TYPES_MAP["SUBMITTED"], None, t_sub, '{"source":"organization_portal"}'),
                                (EVENT_TYPES_MAP["ARRIVED"], current_collector, t_sub + timedelta(minutes=90), '{"logistics":"truck"}'),
                                (EVENT_TYPES_MAP["WEIGHED"], current_sorter, t_sub + timedelta(minutes=105), json.dumps({"weight_kg": weight})),
                                (EVENT_TYPES_MAP["SORTED"], current_sorter, t_sub + timedelta(minutes=120), json.dumps({"is_contaminated": False, "allocations": [{"category_code": stream["category_code"], "weight_kg": weight}]}))
                            ]
                            
                            for ev_type_id, op_id, ev_time, payload in events:
                                await conn.execute(
                                    "INSERT INTO infrastructure.bag_events (bag_id, event_type_id, operator_id, payload, occurred_at) VALUES ($1, $2, $3, $4::jsonb, $5);",
                                    bag_id, ev_type_id, op_id, payload, ev_time
                                )

            current_day += timedelta(days=1)

        print(f"📊 [Simulation Complete] Successfully generated {total_bags} transactional records.", flush=True)
    
    await pool.close()

if __name__ == "__main__":
    asyncio.run(run_global_initialization())
