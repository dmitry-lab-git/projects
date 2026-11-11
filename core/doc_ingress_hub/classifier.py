import json
import logging
from pathlib import Path
from api_manager.service import secure_api_call
from core.db_utils.db_access import get_status_id
from doc_ingress_hub.config import PROMPT_PATH, TRIAGE_MODEL

MAX_TRIAGE_BATCH = 100  # Предохранитель от бесконечной выборки за один запуск


def _parse_triage_json(raw_text: str) -> dict | None:
    if not raw_text:
        return None
    clean = raw_text.strip()
    if clean.startswith("```"):
        parts = clean.split("```")
        clean = parts[1] if len(parts) > 1 else parts[0]
        if clean.startswith("json"):
            clean = clean[4:]
    try:
        return json.loads(clean.strip())
    except Exception as e:
        logging.error(f"[Classifier] Ошибка парсинга JSON: {e}. Сырой ответ: {raw_text[:100]}...")
        return None


def run_ai_triage(conn, client) -> int:
    """Процесс 2: Защищенная AI-классификация документов (doc_type = 'PENDING')."""
    prompt_text = PROMPT_PATH.read_text(encoding="utf-8")
    classified_count = 0
    seen_ids = set()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, file_path, file_name
            FROM processing.source_files
            WHERE doc_type = 'PENDING'
            ORDER BY created_at ASC
            LIMIT %s
        """, (MAX_TRIAGE_BATCH,))
        pending_rows = cur.fetchall()

    if not pending_rows:
        logging.info("[Classifier] Нет новых файлов для AI-классификации.")
        return 0

    status_ready_id = get_status_id(conn, "source_files", "READY_TO_SEND")
    status_unknown_id = get_status_id(conn, "source_files", "UNKNOWN")
    status_classified_id = get_status_id(conn, "source_files", "CLASSIFIED")
    status_deleted_id = get_status_id(conn, "source_files", "DELETED")
    status_error_id = get_status_id(conn, "source_files", "API_ERROR")

    for file_uuid, file_path, file_name in pending_rows:
        uid_str = str(file_uuid)
        if uid_str in seen_ids:
            logging.critical(f"[Classifier] Повторный ID в выборке: {uid_str}. Прерываем цикл.")
            break
        seen_ids.add(uid_str)

        # Защита: проверяем физическое наличие файла до вызова API
        if not file_path or not Path(file_path).exists():
            logging.warning(f"[Classifier] Файл {file_name} отсутствует на диске. Статус -> DELETED.")
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE processing.source_files
                    SET doc_type = 'UNKNOWN', status_id = %s, reject_reason = 'Missing file on disk during triage'
                    WHERE id = %s
                """, (status_deleted_id, file_uuid))
            conn.commit()
            continue

        logging.info(f"[Classifier] Классификация файла: {file_name} ({uid_str})")
        try:
            response = secure_api_call(
                client=client,
                prompt_text=prompt_text,
                conn=conn,
                source_uuid=uid_str,
                model_name=TRIAGE_MODEL,
                target_name="doc_triage",
                file_path=file_path
            )

            if not response:
                raise RuntimeError("Пустой ответ от secure_api_call")

            data = _parse_triage_json(response)
            if not data:
                doc_type = "UNKNOWN"
                doc_title = "UNKNOWN"
            else:
                doc_type = str(data.get("doc_type", "UNKNOWN")).upper().strip()
                doc_title = data.get("doc_title") or "UNKNOWN"

            if doc_type == "RECEIPT":
                target_status_id = status_ready_id
            elif doc_type == "UNKNOWN":
                target_status_id = status_unknown_id
            else:
                target_status_id = status_classified_id

            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE processing.source_files
                    SET doc_type = %s, doc_title = %s, status_id = %s
                    WHERE id = %s
                """, (doc_type, doc_title, target_status_id, file_uuid))

            conn.commit()
            classified_count += 1
            logging.info(f"[Classifier] Готово: {file_name} -> type={doc_type}, title='{doc_title}'")

        except Exception as e:
            conn.rollback()
            logging.error(f"[Classifier] Сбой на файле {uid_str}: {e}. Переводим в API_ERROR.")
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE processing.source_files
                    SET status_id = %s, reject_reason = %s
                    WHERE id = %s
                """, (status_error_id, f"Triage error: {str(e)[:200]}", file_uuid))
            conn.commit()

    return classified_count
