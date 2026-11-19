# Воркер — тонкая обертка, логика в core/trafic_tracker
import sys
from pathlib import Path

# ~/Projects в sys.path, чтобы core был виден из Ledger
sys.path.insert(0, str(Path(__file__).resolve().parents[6]))

from core.trafic_tracker import check_traffic_limit

if __name__ == "__main__":
    print(check_traffic_limit())