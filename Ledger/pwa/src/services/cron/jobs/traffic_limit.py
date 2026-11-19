# src/services/cron/jobs/traffic_limit.py
import json
import os
import smtplib
import subprocess
from datetime import date
from email.mime.text import MIMEText
from pathlib import Path

# ---- Настройки ----
DAILY_LIMIT_MB = 333  # 10 GB / 30 дней
STATE_FILE = Path(__file__).parent / ".traffic-state.json"
THRESHOLDS = [50, 70, 100]

# Твой env, который уже есть - С ТОЧКОЙ
ENV_FILE = Path("/home/fujitsu-u745/Projects/secure_folder/pwa_workers_inspector/.env")

def _load_env():
    if not ENV_FILE.exists():
        print(f"ENV не найден: {ENV_FILE}")
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

_load_env()

# ---- Получение трафика из Windows ----
def _get_windows_traffic_mb() -> float:
    ps_script = (
        "Get-NetAdapterStatistics | "
        "Where-Object { $_.Name -match 'Wi-Fi|WLAN|AndroidAP' } | "
        "Measure-Object -Property ReceivedBytes -Sum | "
        "Select-Object -ExpandProperty Sum"
    )
    try:
        out = subprocess.check_output(
            ["powershell.exe", "-NoProfile", "-Command", ps_script],
            text=True,
            timeout=15
        ).strip()
        return int(out) / 1024 / 1024
    except Exception as e:
        print(f"Ошибка получения трафика из Windows: {e}")
        return 0.0

# ---- Состояние ----
def _load_state():
    today = date.today().isoformat()
    if STATE_FILE.exists():
        try:
            s = json.loads(STATE_FILE.read_text())
            if s.get("date") == today:
                return s
        except Exception:
            pass
    return {"date": today, "baselineMB": _get_windows_traffic_mb(), "notified": []}

# ---- Почта ----
def _send_email(subject: str, body: str):
    to = os.getenv("EMAIL_USER", "d3698627@gmail.com")
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS", "")
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "465"))

    if not user or not password:
        print("Почта не отправлена: нет EMAIL_USER / EMAIL_PASS в env")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = to

    try:
        with smtplib.SMTP_SSL(host, port) as server:
            server.login(user, password)
            server.send_message(msg)
        print(f"Письмо отправлено на {to}")
    except Exception as e:
        print(f"Ошибка отправки почты: {e}")

# ---- Уведомление: тост + почта ----
def _notify(percent: int, used_mb: float):
    msg = f"Трафик ПК: {percent}% - {used_mb:.0f} MB из {DAILY_LIMIT_MB} MB."
    if percent >= 100:
        msg += " Всё, иди кушать, посуду мыть!"

    print(msg)

    # 1. Тост в Windows - встроенный, без BurntToast
    try:
        ps_toast = (
            "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType=WindowsRuntime] | Out-Null; "
            "$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); "
            "$template.GetElementsByTagName('text')[0].AppendChild($template.CreateTextNode('Лимит трафика')) | Out-Null; "
            f"$template.GetElementsByTagName('text')[1].AppendChild($template.CreateTextNode('{msg}')) | Out-Null; "
            "$toast = [Windows.UI.Notifications.ToastNotification]::new($template); "
            "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Traffic Limit').Show($toast);"
        )
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", ps_toast],
            timeout=10
        )
    except Exception as e:
        print(f"Тост не отправился: {e}")

    # 2. Почта
    _send_email(f"Трафик ПК: {percent}%", msg)

# ---- Главная функция для APScheduler ----
def check_traffic_limit():
    state = _load_state()
    now_mb = _get_windows_traffic_mb()
    used_mb = now_mb - state["baselineMB"]
    if used_mb < 0:
        state["baselineMB"] = now_mb
        used_mb = 0

    percent = (used_mb / DAILY_LIMIT_MB) * 100

    for t in THRESHOLDS:
        if percent >= t and t not in state["notified"]:
            _notify(t, used_mb)
            state["notified"].append(t)

    STATE_FILE.write_text(json.dumps(state))
    return {"usedMB": round(used_mb, 1), "percent": round(percent, 1)}

if __name__ == "__main__":
    print(check_traffic_limit())