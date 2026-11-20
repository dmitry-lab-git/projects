# main.py
import time
from agent import check_traffic_limit
from config import INTERVAL_SECONDS

if __name__ == "__main__":
    print("ПК-агент запущен. Отправка TOTAL на телефон...")
    while True:
        check_traffic_limit()
        time.sleep(INTERVAL_SECONDS)