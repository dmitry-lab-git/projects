"""Точка входа консольного чата и ночного автономного запуска агента."""
import argparse
import logging
import os
import sys
import uuid
from pathlib import Path

_CORE = Path(__file__).resolve().parents[3]
_PROJECTS = _CORE.parent
sys.path[:] = [p for p in sys.path if not p or Path(p).resolve() != _PROJECTS]
if str(_CORE) not in sys.path:
    sys.path.insert(0, str(_CORE))

from google import genai
from doc_ingress_hub.config import get_ingress_db_connection
from agent_runner import make_secure_caller
import fs_tools
from session_store import ContextStore, ResponseCache, SessionLogger
from workspace_module.chat.history_manager import HistoryManager
from workspace_module.chat.session_runner import (
    compact_if_needed,
    make_event_handler,
    run_chat_loop,
    run_overnight_loop,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--source-uuid")
    ap.add_argument("--state-dir", default=".cto_agent", help="Каталог лога, контекста и кеша")
    ap.add_argument("--fresh", action="store_true", help="Начать с пустого контекста")
    ap.add_argument("--no-cache", action="store_true", help="Отключить кеш ответов модели")
    ap.add_argument("--cache-ttl", type=int, default=3600, help="TTL кеша в секундах")
    ap.add_argument("--overnight", action="store_true", help="Ночной автономный цикл без пауз")
    ap.add_argument("--max-cycles", type=int, default=200, help="Максимум циклов в ночном режиме")
    ap.add_argument("--step-limit", type=int, default=12, help="Лимит шагов в одном вызове агента")
    ap.add_argument("--sleep-on-error", type=float, default=5.0, help="Пауза при ошибке/503 (сек)")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", force=True)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit(
            "GEMINI_API_KEY не найден: проверьте secure_folder/data_ingress/.env "
            "(его читает doc_ingress_hub.config)."
        )

    state_dir = Path(args.state_dir).expanduser().resolve()
    ctx_store = ContextStore(state_dir / "context.json")
    cache = ResponseCache(
        cache_path=state_dir / "cache.json",
        roots=fs_tools.ROOTS,
        ttl_sec=args.cache_ttl,
        enabled=not args.no_cache,
    )
    source_uuid = args.source_uuid or str(uuid.uuid4())
    logger = SessionLogger(state_dir / "events.jsonl", source_uuid=source_uuid)
    hm = HistoryManager(token_threshold=15_000, keep_recent=6)

    if args.fresh:
        ctx_store.clear()
        history: list = []
    else:
        history = compact_if_needed(hm, ctx_store.load())

    print(f"source_uuid этой сессии: {source_uuid}")
    print(f"Хранилище сессии: {state_dir} (сообщений в контексте: {len(history)})")

    client = genai.Client(api_key=api_key)
    conn = get_ingress_db_connection()
    try:
        raw_call = make_secure_caller(client, conn, source_uuid)
        call = cache.wrap_caller(
            raw_call,
            target_name="technical",
            on_hit=lambda: print("  [cache] ответ взят из локального кеша"),
        )
        on_event = make_event_handler(logger)

        if args.overnight:
            run_overnight_loop(
                question=args.question,
                call=call,
                history=history,
                hm=hm,
                ctx_store=ctx_store,
                logger=logger,
                on_event=on_event,
                max_cycles=args.max_cycles,
                step_limit=args.step_limit,
                sleep_on_error=args.sleep_on_error,
            )
        else:
            print("Режим чата активен. Введите /help для списка команд или /exit для выхода.")
            run_chat_loop(
                initial_question=args.question,
                call=call,
                history=history,
                source_uuid=source_uuid,
                hm=hm,
                ctx_store=ctx_store,
                cache=cache,
                logger=logger,
                on_event=on_event,
                step_limit=args.step_limit,
            )
    finally:
        if conn and not conn.closed:
            conn.close()


if __name__ == "__main__":
    main()