import hashlib
import logging
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from core.db_utils.db_access import get_status_id
from doc_ingress_hub.config import INGRESS_ROOT, ARCHIVE_STORAGE
from doc_ingress_hub.compressor import compress_to_blob


def calculate_sha256(file_path: Path) -> str:
    """Вычисляет SHA-256 хэш файла потоково (блоками по 8 КБ)."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def detect_ingress_zone(file_path: Path) -> tuple[str, bool]:
    """
    Определяет зону входа и флаг неприкосновенности Important по пути файла.
    Возвращает: (ingress_zone, is_important)
    """
    rel_parts = [p.lower() for p in file_path.relative_to(INGRESS_ROOT).parts]
    if "important" in rel_parts:
        return "receipts_income/Important", True
    if "receipts_income" in rel_parts:
        return "receipts_income", False
    return "root_unsorted", False


def run_ingestion(conn) -> int:
    """
    Процесс 1: Захват файлов из Ingress, сжатие в BLOB и запись в БД.
    Возвращает количество успешно принятых новых файлов.
    """
    if not INGRESS_ROOT.exists():
        logging.warning(f"[Ingestor] Директория Ingress не найдена: {INGRESS_ROOT}")
        return 0

    ARCHIVE_STORAGE.mkdir(parents=True, exist_ok=True)
    files = [
        f for f in INGRESS_ROOT.rglob("*")
        if f.is_file() and not f.name.startswith(".") and f.name.lower() != "thumbs.db"
    ]

    if not files:
        logging.info("[Ingestor] Папка Ingress пуста. Новых файлов нет.")
        return 0

    ingested_count = 0
    status_ingested_id = get_status_id(conn, "source_files", "INGESTED")

    for file_path in files:
        file_hash = calculate_sha256(file_path)
        zone, is_important = detect_ingress_zone(file_path)

        try:
            with conn.cursor() as cur:
                # 1. Проверка на дубликат по SHA-256
                cur.execute(
                    "SELECT id FROM processing.source_files WHERE file_hash = %s",
                    (file_hash,)
                )
                if cur.fetchone():
                    logging.info(f"[Ingestor] Дубликат пропущен (хэш уже в БД): {file_path.name}")
                    if not is_important:
                        file_path.unlink()
                    continue

                # 2. Сжатие файла в BLOB
                blob_data, mime_type, orig_size, comp_size = compress_to_blob(file_path)
                ratio = round((1 - comp_size / orig_size) * 100, 2) if orig_size > 0 else 0

                file_uuid = str(uuid.uuid4())
                now = datetime.now()

                # Определяем целевой путь хранения на диске (Important не перемещаем!)
                if is_important:
                    final_path = str(file_path)
                else:
                    dest_dir = ARCHIVE_STORAGE / now.strftime("%Y-%m-%d")
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    final_path = str(dest_dir / f"{file_uuid}_{file_path.name}")

                # 3. Запись метаданных в processing.source_files
                cur.execute(
                    """
                    INSERT INTO processing.source_files
                        (id, file_name, file_path, file_size, created_at, status_id,
                         file_hash, ingress_zone, is_important, doc_type, doc_title)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING', %s)
                    """,
                    (
                        file_uuid, file_path.name, final_path, orig_size, now,
                        status_ingested_id, file_hash, zone, is_important, file_path.name
                    )
                )

                # 4. Запись сжатого BLOB в processing.source_file_blobs
                cur.execute(
                    """
                    INSERT INTO processing.source_file_blobs
                        (source_file_id, compressed_data, mime_type, original_size,
                         compressed_size, compression_ratio, is_protected)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (file_uuid, blob_data, mime_type, orig_size, comp_size, ratio, is_important)
                )

            conn.commit()

            # 5. Перемещение файла на диске строго после commit() в PostgreSQL
            if not is_important:
                shutil.move(str(file_path), final_path)
                logging.info(
                    f"[Ingestor] Принят ({zone}): {file_path.name} -> "
                    f"сжатие {ratio}%, перенесен в буфер."
                )
            else:
                logging.info(
                    f"[Ingestor] Принят [IMPORTANT]: {file_path.name} -> "
                    f"защищен в БД и оставлен в Important."
                )

            ingested_count += 1

        except Exception as e:
            conn.rollback()
            logging.error(f"[Ingestor] Ошибка при индексации {file_path.name}: {e}")

    return ingested_count
