import json, subprocess, time, urllib.request
from datetime import date
from .config import DAILY_LIMIT_MB, STATE_FILE, PHONE_URL, THRESHOLDS
from .db import get_db

def _get_one(prop: str) -> int:
    ps = (
        f"Get-NetAdapterStatistics | "
        f"Where-Object {{ $_.Name -match 'Wi-Fi|WLAN|AndroidAP' }} | "
        f"Measure-Object -Property {prop} -Sum | Select-Object -ExpandProperty Sum"
    )
    try:
        out = subprocess.check_output(
            ["powershell.exe", "-NoProfile", "-Command", ps],
            text=True, timeout=10
        ).strip()
        return int(out) if out else 0
    except Exception:
        return 0

def _get_windows_traffic():
    return _get_one("ReceivedBytes"), _get_one("SentBytes")  # down, up

def _load_state():
    today = date.today().isoformat()
    if STATE_FILE.exists():
        try:
            s = json.loads(STATE_FILE.read_text())
            if s.get("date") == today:
                return s
        except Exception:
            pass
    down, up = _get_windows_traffic()
    return {"date": today, "baseline_up": up, "baseline_down": down, "notified": []}

def _send_to_phone(up_delta: int, down_delta: int):
    payload = json.dumps({
        "device_id": "pc",
        "timestamp": int(time.time() * 1000),
        "bytes_up_total": up_delta,
        "bytes_down_total": down_delta,
    }).encode()
    try:
        req = urllib.request.Request(PHONE_URL, data=payload, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=3)
    except Exception as e:
        print(f"Телефон недоступен: {e}")

def check_traffic_limit():
    state = _load_state()
    down_now, up_now = _get_windows_traffic()
    if down_now < state["baseline_down"] or up_now < state["baseline_up"]:
        state["baseline_down"], state["baseline_up"] = down_now, up_now
        state["notified"] = []
    down_delta = down_now - state["baseline_down"]
    up_delta = up_now - state["baseline_up"]
    used_mb = (down_delta + up_delta) / 1024 / 1024
    percent = (used_mb / DAILY_LIMIT_MB) * 100

    conn = get_db()
    conn.execute(
        "INSERT INTO traffic_log (timestamp, app_name, bytes_up, bytes_down) VALUES (?, ?, ?, ?)",
        (int(time.time() * 1000), "TOTAL", up_delta, down_delta),
    )
    conn.commit()
    conn.close()

    _send_to_phone(up_delta, down_delta)

    for t in THRESHOLDS:
        if percent >= t and t not in state["notified"]:
            print(f"Трафик ПК: {t}% - {used_mb:.0f} MB из {DAILY_LIMIT_MB} MB.")
            state["notified"].append(t)

    state["baseline_down"], state["baseline_up"] = down_now, up_now
    STATE_FILE.write_text(json.dumps(state))
    return {"usedMB": round(used_mb, 1), "percent": round(percent, 1)}