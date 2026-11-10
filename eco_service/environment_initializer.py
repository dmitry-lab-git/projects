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

# Фиксированные UUID системных событий жизненного цикла мешка
EVENT_TYPES_MAP = {
    "SUBMITTED": uuid.UUID("fa4e5b22-8356-42d4-bb9e-4e4bf7e9b0e1"),
    "ARRIVED": uuid.UUID("3c2b81fa-9d1a-4d24-82a1-5fe11c784ab2"),
    "WEIGHED": uuid.UUID("9f8e7d6c-5b4a-4321-bd23-1a2b3c4d5e6f"),
    "SORTED": uuid.UUID("da2a13f5-62bb-4c22-b5e1-8f4b7a2c3d10")
}

async def run_global_initialization():
    print("Opening connection pool for streamlined simulation...", flush=True)
    pool = await create_database_pool()
    
    async with pool.acquire() as conn:
        # 1. Очищаем только транзакционные таблицы перед симуляцией
        print(" [1/3] Truncating transaction logs (bags & events)...", flush=True)
        await conn.execute("TRUNCATE TABLE infrastructure.bag_events CASCADE;")
        await conn.execute("TRUNCATE TABLE infrastructure.bags CASCADE;")

        # 2. Вытягиваем необходимые сущности из справочников БД
        print("📥 [2/3] Fetching reference entities from database...", flush=True)
        
        yards_db = await conn.fetch("SELECT yard_id FROM dicts.yards WHERE is_active = TRUE;")
        yard_ids = [row["yard_id"] for row in yards_db]
        if not yard_ids:
            raise ValueError("Error: dicts.yards is empty! Please seed yards before running simulation.")
        
        # Домохозяйства: проецируем user_id как resident_id для infrastructure.bags
        households_db = await conn.fetch("SELECT user_id AS resident_id, yard_id FROM dicts.households;")
        organizations_db = await conn.fetch("SELECT organization_id, business_type FROM dicts.organizations WHERE is_active = TRUE;")
        
        bag_types_db = await conn.fetch("SELECT type_id, code FROM dicts.bag_types;")
        bag_type_map = {row["code"]: row["type_id"] for row in bag_types_db}

        # Получаем пулы активных операторов на основе ролей из model_config
        operators_db = await conn.fetch("SELECT operator_id, role FROM dicts.operators WHERE is_active = TRUE;")
        collector_uuids = [op["operator_id"] for op in operators_db if op["role"] == SIMULATION_OPERATOR_ROLES["COLLECTOR"]]
        sorter_uuids = [op["operator_id"] for op in operators_db if op["role"] == SIMULATION_OPERATOR_ROLES["SORTER"]]

        if not collector_uuids:
            collector_uuids = [uuid.uuid4()]
        if not sorter_uuids:
            sorter_uuids = [uuid.uuid4()]

        # 3. Запуск симуляции по временной шкале
        print("🌊 [3/3] Replaying timeline based on model_config parameters...", flush=True)
        current_day = SIMULATION_START_DATE
        total_bags = 0

        while current_day <= SIMULATION_END_DATE:
            print(f"⏳ Simulating date: {current_day.strftime('%Y-%m-%d')} (Total bags so far: {total_bags})", flush=True)
            
            async with conn.transaction():
                # --- А. Генерация от домохозяйств ---
                for hh in households_db:
                    if random.random() < HOUSEHOLD_DAILY_ACTIVITY_PROBABILITY:
                        total_bags += 1
                        bag_id = uuid.uuid4()
                        t_sub = current_day + timedelta(minutes=random.randint(60, 800))
                        
                        waste_types = list(HOUSEHOLD_WASTE_PROFILE.keys())
                        weights = [HOUSEHOLD_WASTE_PROFILE[wt]["weight"] for wt in waste_types]
                        chosen_wt = random.choices(waste_types, weights=weights)[0]
                        
                        profile = HOUSEHOLD_WASTE_PROFILE[chosen_wt]
                        b_type_uid = bag_type_map.get(chosen_wt)
                        weight = round(random.uniform(*profile["weight_range"]), 3)
                        
                        if not b_type_uid:
                            continue

                        # Динамический выбор исполнителей из пулов справочника
                        current_collector = random.choice(collector_uuids)
                        current_sorter = random.choice(sorter_uuids)

                        # Таблица 1: Создание мешка
                        await conn.execute(
                            "INSERT INTO infrastructure.bags (bag_id, resident_id, yard_id, type_id, created_at) VALUES ($1, $2, $3, $4, $5);",
                            bag_id, hh["resident_id"], hh["yard_id"], b_type_uid, t_sub
                        )
                        
                        # Таблица 2: Цепочка событий жизненного цикла
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

                # --- Б. Генерация от организаций ---
                for org in organizations_db:
                    b_type_code = org["business_type"]
                    waste_streams = ORGANIZATION_WASTE_PROFILES.get(b_type_code, ORGANIZATION_WASTE_PROFILES["OTHER"])
                    
                    for stream in waste_streams:
                        if random.random() < stream["daily_probability"]:
                            total_bags += 1
                            bag_id = uuid.uuid4()
                            t_sub = current_day + timedelta(hours=random.randint(8, 16))
                            random_yard_id = random.choice(yard_ids)
                            
                            b_type_uid = bag_type_map.get(stream["bag_type_code"], bag_type_map.get("CLEAN_DRY"))
                            weight = round(random.uniform(*stream["weight_range"]), 3)
                            
                            org_resident_id = households_db[0]["resident_id"] if households_db else uuid.uuid4()

                            current_collector = random.choice(collector_uuids)
                            current_sorter = random.choice(sorter_uuids)

                            # Таблица 1: Создание мешка
                            await conn.execute(
                                "INSERT INTO infrastructure.bags (bag_id, resident_id, yard_id, type_id, created_at) VALUES ($1, $2, $3, $4, $5);",
                                bag_id, org_resident_id, random_yard_id, b_type_uid, t_sub
                            )
                            
                            # Таблица 2: Цепочка событий
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

        print(f"📊 [Simulation Complete] Successfully generated {total_bags} transactional records across `bags` and `bag_events`.", flush=True)
    
    await pool.close()

if __name__ == "__main__":
    asyncio.run(run_global_initialization())