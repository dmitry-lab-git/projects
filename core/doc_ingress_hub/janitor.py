import logging
from datetime import datetime, timedelta
from doc_ingress_hub.config import ARCHIVE_STORAGE, RETENTION_DAYS


def run_buffer_cleanup(conn) -> int:
    """
    Процесс 4: Очистка локального буфера старше RETENTION_DAYS (90 дней)
    после подтверждения наличия непустого BLOB в PostgreSQL.
    """
    if not ARCHIVE_STORAGE.exists():
        return 0

    cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
    deleted_files = 0

    for date_dir in ARCHIVE_STORAGE.iterdir():
        if not date_dir.is_dir():
            continue

        try:
            dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
        except ValueError:
            continue

        if dir_date >= cutoff_date:
            continue

        for file_path in date_dir.iterdir():
            if not file_path.is_file():
                continue

            # Имя файла в буфере имеет формат <uuid>_<original_name>
            possible_uuid = file_path.name.split("_")[0]

            with conn.cursor() as cur:
                cur.execute("""
                    SELECT b.source_file_id
                    FROM processing.source_file_blobs b
                    JOIN processing.source_files f ON f.id = b.source_file_id
                    WHERE b.source_file_id::text = %s
                      AND octet_length(b.compressed_data) > 0
                      AND f.is_important = false
                """, (possible_uuid,))
                verified_in_db = cur.fetchone()

            if verified_in_db:
                file_path.unlink()
                deleted_files += 1
            else:
                logging.warning(f"[Janitor] Пропущен файл без подтвержденного BLOB в БД: {file_path}")

        # Удаляем пустую папку даты
        if not any(date_dir.iterdir()):
            date_dir.rmdir()

    if deleted_files:
        logging.info(f"[Janitor] Очищено {deleted_files} файлов старше {RETENTION_DAYS} дней.")
    return deleted_files
