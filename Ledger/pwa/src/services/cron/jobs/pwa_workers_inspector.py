import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

PROJECTS_ROOT = Path("/home/fujitsu-u745/Projects")
INSPECTOR_ENV = PROJECTS_ROOT / "secure_folder" / "pwa_workers_inspector" / ".env"
TME_ENV = PROJECTS_ROOT / "secure_folder" / "tme" / ".env"

if not INSPECTOR_ENV.exists():
    raise FileNotFoundError(f"Файл конфигурации не найден: {INSPECTOR_ENV}")

load_dotenv(dotenv_path=INSPECTOR_ENV)
if TME_ENV.exists():
    load_dotenv(dotenv_path=TME_ENV, override=False)

INGRESS_ROOT = Path("/mnt/c/Personal/Projects/Ingress")
BACKUP_ROOT = Path("/mnt/c/Personal/Projects/Archive/db_dump_files")


def get_inspector_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST") or os.getenv("INSPECTOR_DB_HOST", "localhost"),
        port=os.getenv("DB_PORT") or os.getenv("INSPECTOR_DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME") or os.getenv("INSPECTOR_DB_NAME", "ledger"),
        user=os.getenv("DB_USER") or os.getenv("INSPECTOR_DB_USER", "pwa_workers_inspector"),
        password=os.getenv("DB_PASS") or os.getenv("INSPECTOR_DB_PASS")
    )


def check_directory_status(path: Path, max_age_hours: int = 36) -> str:
    if not path.exists():
        return f"ОТСУТСТВУЕТ ({path})"
    files = [f for f in path.rglob("*") if f.is_file() and not f.name.startswith(".")]
    if not files:
        return "Пусто (0 файлов)"
    newest = max(files, key=lambda f: f.stat().st_mtime)
    age_hours = (datetime.now().timestamp() - newest.stat().st_mtime) / 3600
    status = "OK" if age_hours <= max_age_hours else f"УСТАРЕЛ ({int(age_hours)} ч. назад)"
    return f"{status} | Файлов: {len(files)} | Свежий: {newest.name}"


def gather_weekly_report() -> str:
    conn = get_inspector_conn()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    try:
        with conn.cursor() as cur:
            # 1. Статистика doc_ingress_hub за 7 дней
            cur.execute("""
                SELECT st.code, sf.doc_type, COUNT(*)
                FROM processing.source_files sf
                LEFT JOIN dicts.dict_statuses st ON st.id = sf.status_id
                WHERE sf.created_at >= NOW() - INTERVAL '7 days'
                GROUP BY st.code, sf.doc_type
                ORDER BY COUNT(*) DESC;
            """)
            ingress_rows = cur.fetchall()

            # 2. Общий объем BLOB-хранилища
            cur.execute("""
                SELECT COUNT(*),
                       COALESCE(ROUND(SUM(original_size) / 1048576.0, 2), 0),
                       COALESCE(ROUND(SUM(compressed_size) / 1048576.0, 2), 0)
                FROM processing.source_file_blobs;
            """)
            blob_count, orig_mb, comp_mb = cur.fetchone()

            # 3. Оцифрованные чеки за 7 дней
            cur.execute("""
                SELECT COUNT(*), COALESCE(SUM(amount), 0)
                FROM processing.receipts
                WHERE created_at >= NOW() - INTERVAL '7 days';
            """)
            receipts_count, receipts_sum = cur.fetchone()

            # 4. Статистика api_manager за 7 дней
            cur.execute("""
                SELECT st.code, COUNT(*), COALESCE(SUM(input_tokens + COALESCE(output_tokens, 0)), 0)
                FROM processing.api_requests_log l
                LEFT JOIN dicts.dict_statuses st ON st.id = l.status_id
                WHERE l.created_at >= NOW() - INTERVAL '7 days'
                GROUP BY st.code
                ORDER BY COUNT(*) DESC;
            """)
            api_rows = cur.fetchall()
    finally:
        conn.close()

    ingress_disk = check_directory_status(INGRESS_ROOT, max_age_hours=24)
    backups_disk = check_directory_status(BACKUP_ROOT, max_age_hours=36)

    ingress_html = "".join(
        f"<tr><td>{status_code or '-'}</td><td>{doc_type or '-'}</td><td><b>{cnt}</b></td></tr>"
        for status_code, doc_type, cnt in ingress_rows
    ) or "<tr><td colspan='3'>Новых файлов за 7 дней не было</td></tr>"

    api_html = "".join(
        f"<tr><td>{status_code or '-'}</td><td><b>{cnt}</b></td><td>{tokens:,}</td></tr>"
        for status_code, cnt, tokens in api_rows
    ) or "<tr><td colspan='3'>Запросов к API за 7 дней не было</td></tr>"

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #222; line-height: 1.5;">
        <h2>Еженедельный акт инспекции фоновых воркеров ({now_str})</h2>
        <p>Инспектор: <code>pwa_workers_inspector</code></p>

        <h3>1. Состояние дисковых контуров и бэкапов</h3>
        <ul>
            <li><b>Windows Ingress:</b> {ingress_disk}</li>
            <li><b>Бэкапы БД (Archive):</b> {backups_disk}</li>
            <li><b>Реестр BLOB в PostgreSQL:</b> {blob_count} файлов ({orig_mb} МБ сжато в <b>{comp_mb} МБ</b>)</li>
        </ul>

        <h3>2. Прием и классификация (doc_ingress_hub за 7 дней)</h3>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;">
            <tr style="background: #f2f2f2;"><th>Статус файла</th><th>Тип (AI)</th><th>Кол-во</th></tr>
            {ingress_html}
        </table>

        <h3>3. Оцифровка чеков (receipts_processor за 7 дней)</h3>
        <p>Добавлено чеков в БД: <b>{receipts_count}</b> на общую сумму <b>{receipts_sum:,.2f}</b></p>

        <h3>4. Здоровье AI-шлюза (api_manager за 7 дней)</h3>
        <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;">
            <tr style="background: #f2f2f2;"><th>Статус вызова</th><th>Запросов</th><th>Токенов</th></tr>
            {api_html}
        </table>
    </body>
    </html>
    """


def send_email_report(html_body: str):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_user = os.getenv("EMAIL_USER") or os.getenv("SMTP_USER")
    smtp_pass = os.getenv("EMAIL_PASS") or os.getenv("SMTP_APP_PASSWORD")
    recipient = os.getenv("REPORT_RECIPIENT") or smtp_user or "d3698627@gmail.com"

    if not smtp_user or not smtp_pass:
        raise ValueError("Не заданы EMAIL_USER или EMAIL_PASS в .env")

    msg = EmailMessage()
    msg["Subject"] = f"[Ledger Ops] Еженедельный отчет инспектора воркеров ({datetime.now().strftime('%Y-%m-%d')})"
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg.set_content("Для просмотра отчета включите отображение HTML в почтовом клиенте.")
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)


if __name__ == "__main__":
    report_html = gather_weekly_report()
    send_email_report(report_html)
    print(f"[{datetime.now()}] Отчет инспектора успешно отправлен на почту.")
