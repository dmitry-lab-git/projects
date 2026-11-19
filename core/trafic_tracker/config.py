from pathlib import Path
DAILY_LIMIT_MB = 333  # 10 GB / 30 дней
BASE_DIR = Path(__file__).parent
DB_FILE = BASE_DIR / "traffic_pc.db"
STATE_FILE = BASE_DIR / ".traffic-state.json"
PHONE_URL = "http://192.168.43.1:8080/api/v1/report"
THRESHOLDS = [50, 70, 100]