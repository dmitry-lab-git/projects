import reflex as rx
from typing import Dict, Any, List
from .base import AppState

class AnalyticsState(AppState):
    """State for fetching and managing 5 analytical data marts."""
    kpi_summary: Dict[str, Any] = {}
    daily_trends: List[Dict[str, Any]] = []
    waste_by_category: List[Dict[str, Any]] = []
    yard_performance: List[Dict[str, Any]] = []
    operator_performance: List[Dict[str, Any]] = []

    is_loading: bool = False
    error_message: str = ""

    async def fetch_analytics_data(self):
        """Asynchronously query the database with verbose debug console output."""
        if self.is_loading:
            return
            
        self.is_loading = True
        self.error_message = ""
        print("\n--- [DEBUG ANALYTICS] Fetching data started ---")

        try:
            pool = await self.get_pool()
            async with pool.acquire() as conn:
                # 1. KPI Summary
                try:
                    kpi_row = await conn.fetchrow("SELECT * FROM analytics.v_kpi_summary;")
                    self.kpi_summary = dict(kpi_row) if kpi_row else {}
                    print(f"[DEBUG ANALYTICS] v_kpi_summary fetched: {self.kpi_summary}")
                except Exception as e:
                    print(f"[ERROR ANALYTICS] Error in v_kpi_summary: {e}")

                # 2. Daily Trends
                try:
                    trends_rows = await conn.fetch(
                        "SELECT * FROM analytics.v_daily_trends ORDER BY log_date ASC LIMIT 30;"
                    )
                    self.daily_trends = [dict(r) for r in trends_rows]
                    print(f"[DEBUG ANALYTICS] v_daily_trends rows: {len(self.daily_trends)}")
                except Exception as e:
                    print(f"[ERROR ANALYTICS] Error in v_daily_trends: {e}")

                # 3. Waste by Category
                try:
                    cat_rows = await conn.fetch("SELECT * FROM analytics.v_waste_by_category;")
                    self.waste_by_category = [dict(r) for r in cat_rows]
                    print(f"[DEBUG ANALYTICS] v_waste_by_category rows: {len(self.waste_by_category)}")
                except Exception as e:
                    print(f"[ERROR ANALYTICS] Error in v_waste_by_category: {e}")

                # 4. Yard Performance
                try:
                    yard_rows = await conn.fetch(
                        "SELECT * FROM analytics.v_yard_performance ORDER BY total_weight_kg DESC;"
                    )
                    self.yard_performance = [dict(r) for r in yard_rows]
                    print(f"[DEBUG ANALYTICS] v_yard_performance rows: {len(self.yard_performance)}")
                except Exception as e:
                    print(f"[ERROR ANALYTICS] Error in v_yard_performance: {e}")

                # 5. Operator Performance
                try:
                    op_rows = await conn.fetch("SELECT * FROM analytics.v_operator_performance;")
                    self.operator_performance = [dict(r) for r in op_rows]
                    print(f"[DEBUG ANALYTICS] v_operator_performance rows: {len(self.operator_performance)}")
                except Exception as e:
                    print(f"[ERROR ANALYTICS] Error in v_operator_performance: {e}")

        except Exception as e:
            self.error_message = f"DB connection failed: {str(e)}"
            print(f"[ERROR ANALYTICS] Connection pool global failure: {e}")
        finally:
            self.is_loading = False
            print("--- [DEBUG ANALYTICS] Fetching data completed ---\n")
