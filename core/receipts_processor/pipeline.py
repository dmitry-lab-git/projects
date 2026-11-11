# receipts_processor/pipeline.py
import core
print("Пакет core импортируется из:", core.__file__)
import os
import logging
import json
import uuid
import random
from api_manager.service import secure_api_call
from api_manager.exceptions import ExceptionHandler
from core.db_utils.db_access import get_db_connection, db_execute, db_fetch_val, db_fetch_row, get_status_id
from receipts_processor.document_processor import DocumentProcessor
from receipts_processor.prompt_manager import PROMPT_CONTENT
from receipts_processor.status_manager import StatusRegistry

MAX_ITERATIONS = 200  # Жесткий предохранитель от бесконечного цикла за один запуск


def safe_parse_json(result):
    if not result:
        logging.error("safe_parse_json: Получен пустой результат от API.")
        return None
    if isinstance(result, (dict, list)):
        return result
    try:
        clean_result = result.strip()
        if clean_result.startswith('```'):
            clean_result = clean_result.split('```')
            clean_result = clean_result[1] if len(clean_result) > 1 else clean_result[0]
            if clean_result.startswith('json'):
                clean_result = clean_result[4:]
            clean_result = clean_result.strip()
        return json.loads(clean_result)
    except Exception as e:
        logging.error(f"safe_parse_json: Ошибка парсинга: {e}. Сырой ответ: {result[:100]}...")
        return None


def run_receipts_pipeline(client, prompt_text):
    conn = get_db_connection()
    registry = StatusRegistry(conn)
    seen_ids = set()
    iterations = 0

    try:
        status_legal = db_fetch_val(conn, "GET_STATUS_ID", ('UNVERIFIED', 'legal_entities'))
        status_receipt = db_fetch_val(conn, "GET_STATUS_ID", ('NEW', 'receipts'))
        status_deleted = get_status_id(conn, 'source_files', 'DELETED')
        status_processing = get_status_id(conn, 'source_files', 'PROCESSING')
        status_api_error = get_status_id(conn, 'source_files', 'API_ERROR')
        status_needs_review = get_status_id(conn, 'source_files', 'NEEDS_REVIEW')
        status_finished = get_status_id(conn, 'source_files', 'FINISHED')

        while iterations < MAX_ITERATIONS:
            iterations += 1
            file_record = db_fetch_row(conn, "GET_NEXT_UNPROCESSED_FILE", ())
            if not file_record:
                logging.info("Очередь пуста. Все файлы обработаны.")
                break

            file_uuid = str(file_record.get('id') or file_record.get('file_uuid'))
            file_path = file_record.get('file_path')

            # 1. Защита от повторной выборки одного и того же ID (анти-зацикливание)
            if file_uuid in seen_ids:
                logging.critical(f"АВАРИЙНАЯ ОСТАНОВКА: Файл {file_uuid} повторно попал в выборку! Проверьте UPDATE_FILE_STATUS.")
                break
            seen_ids.add(file_uuid)

            # 2. Защита от отсутствующих на диске файлов (переводим в DELETED без вызова API)
            if not file_path or not os.path.exists(file_path):
                logging.warning(f"Файл {file_uuid} не найден на диске ({file_path}). Переводим в статус DELETED.")
                with conn:
                    db_execute(conn, "UPDATE_FILE_STATUS", (status_deleted, file_uuid))
                continue

            logging.info(f"Взят в работу файл [{iterations}/{MAX_ITERATIONS}]: {file_uuid}")

            try:
                # Статус PROCESSING
                with conn:
                    db_execute(conn, "UPDATE_FILE_STATUS", (status_processing, file_uuid))

                result = secure_api_call(
                    client=client,
                    prompt_text=prompt_text,
                    conn=conn,
                    source_uuid=file_uuid,
                    file_path=file_path
                )

                if not result:
                    logging.warning(f"Файл {file_uuid}: API не вернул данные.")
                    with conn:
                        db_execute(conn, "UPDATE_FILE_STATUS", (status_api_error, file_uuid))
                    continue

                receipt_data = safe_parse_json(result)
                if not receipt_data:
                    logging.error(f"Файл {file_uuid}: Не удалось распарсить JSON.")
                    with conn:
                        db_execute(conn, "UPDATE_FILE_STATUS", (status_needs_review, file_uuid))
                    continue

                documents = receipt_data.get("extracted_documents", [])
                if not documents:
                    logging.warning(f"Файл {file_uuid}: Документ не содержит распознанных чеков (extracted_documents пуст).")
                    with conn:
                        db_execute(conn, "UPDATE_FILE_STATUS", (status_needs_review, file_uuid))
                    continue

                with conn:
                    for doc in documents:
                        success, error = DocumentProcessor.process_and_save(conn, doc, file_uuid, status_receipt, status_legal)
                        if not success:
                            logging.error(f"Файл {file_uuid}: {error}")
                            continue

                    db_execute(conn, "UPDATE_FILE_STATUS", (status_finished, file_uuid))
                    logging.info(f"Файл {file_uuid} успешно завершен.")

            except json.JSONDecodeError as jde:
                conn.rollback()
                logging.error(f"Ошибка парсинга JSON для файла {file_uuid}: {jde}")
                with conn:
                    db_execute(conn, "UPDATE_FILE_STATUS", (status_needs_review, file_uuid))
            except Exception as e:
                conn.rollback()
                with conn:
                    db_execute(conn, "UPDATE_FILE_STATUS", (status_api_error, file_uuid))
                logging.error(f"Файл {file_uuid} завершился с ошибкой: {e}")

        if iterations >= MAX_ITERATIONS:
            logging.warning(f"Достигнут лимит итераций ({MAX_ITERATIONS}) за один запуск. Остаток очереди будет обработан при следующем запуске.")

    finally:
        conn.close()


if __name__ == "__main__":
    from google import genai
    from dotenv import load_dotenv
    load_dotenv("/home/fujitsu-u745/Projects/secure_folder/api_manager/.env")
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    logging.basicConfig(level=logging.INFO, force=True)
    run_receipts_pipeline(client, PROMPT_CONTENT)
