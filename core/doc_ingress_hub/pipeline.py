import logging
import os
from google import genai

from doc_ingress_hub.config import get_ingress_db_connection
from doc_ingress_hub.ingestor import run_ingestion
from doc_ingress_hub.classifier import run_ai_triage
from doc_ingress_hub.janitor import run_buffer_cleanup
from receipts_processor.pipeline import run_receipts_pipeline
from receipts_processor.prompt_manager import PROMPT_CONTENT as RECEIPT_PROMPT


def run_master_pipeline():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY не найден в secure_folder/data_ingress/.env")

    client = genai.Client(api_key=api_key)
    conn = get_ingress_db_connection()

    try:
        logging.info("=== ЭТАП 1: Захват файлов из Ingress и запись BLOB ===")
        run_ingestion(conn)

        logging.info("=== ЭТАП 2: AI-классификация и индексация (Triage) ===")
        run_ai_triage(conn, client)

        logging.info("=== ЭТАП 4: Очистка буфера старше 90 дней ===")
        run_buffer_cleanup(conn)
    except Exception as e:
        logging.error(f"[MasterPipeline] Ошибка на этапах doc_ingress_hub: {e}", exc_info=True)
    finally:
        if conn and not conn.closed:
            conn.close()

    logging.info("=== ЭТАП 3: Запуск предметного обработчика чеков (receipts_processor) ===")
    try:
        run_receipts_pipeline(client, RECEIPT_PROMPT)
    except Exception as e:
        logging.error(f"[MasterPipeline] Ошибка в receipts_processor: {e}", exc_info=True)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        force=True
    )
    run_master_pipeline()
