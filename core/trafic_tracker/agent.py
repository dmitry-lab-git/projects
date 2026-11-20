# agent.py
import time
import json
import subprocess
import urllib.request
from .config import PHONE_URL

# В памяти храним предыдущие показания адаптера
_last_down = 0
_last_up = 0

def _get_windows_traffic():
    """Возвращает (down, up) в байтах с Wi-Fi/раздачи."""
    ps = (
        "Get-NetAdapterStatistics | "
        "Where-Object { $_.Name -match 'Wi-Fi|WLAN|AndroidAP' } | "
        "Measure-Object -Property ReceivedBytes, SentBytes -Sum | "
        "Select-Object -ExpandProperty Sum"
    )
    try:
        out = subprocess.check_output(
            ["powershell.exe", "-NoProfile", "-Command", ps],
            text=True, timeout=10
        ).strip()
        # PowerShell вернет два числа (ReceivedBytes, SentBytes) через пробел или перевод строки
        parts = out.split()
        if len(parts) >= 2:
            return int(parts[0]), int(parts[1]) # down, up
        return 0, 0
    except Exception as e:
        print(f"Ошибка чтения адаптера: {e}")
        return 0, 0

def _send_to_phone(up_delta: int, down_delta: int):
    payload = json.dumps({
        "device_id": "pc",
        "timestamp": int(time.time() * 1000),
        "total": {
            "bytes_up_delta": up_delta,
            "bytes_down_delta": down_delta
        }
    }).encode()
    
    try:
        req = urllib.request.Request(PHONE_URL, data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=3)
    except Exception as e:
        print(f"Телефон недоступен: {e}")

def check_traffic_limit():
    global _last_down, _last_up
    
    down_now, up_now = _get_windows_traffic()
    
    # Первый запуск или перезагрузка (счетчики обнулились)
    if _last_down == 0 or down_now < _last_down:
        _last_down, _last_up = down_now, up_now
        return

    down_delta = down_now - _last_down
    up_delta = up_now - _last_up
    
    # Если трафик реально был (чтобы не спамить нулями)
    if down_delta > 0 or up_delta > 0:
        _send_to_phone(up_delta, down_delta)
    
    _last_down, _last_up = down_now, up_now