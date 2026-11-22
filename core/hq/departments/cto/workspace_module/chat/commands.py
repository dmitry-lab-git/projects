"""Обработка slash-команд интерактивного чата."""
import json
from pathlib import Path
from typing import Tuple

from session_store import ContextStore, ResponseCache, SessionLogger
from workspace_module.chat.history_manager import HistoryManager

HELP_TEXT = """Команды чата:
  /help                  - показать эту справку
  /context               - показать количество сообщений и оценку токенов
  /compact               - сжать историю в памяти при пороге 15k (без потери сути)
  /reset                 - очистить контекст диалога (и файл context.json)
  /cache [on|off|clear]  - статистика или управление кешем ответов
  /paths                 - показать пути к context.json, events.jsonl и cache.json
  /uuid                  - показать текущий source_uuid
  /save <путь.json>      - сохранить текущую историю в файл
  /load <путь.json>      - импортировать историю из файла
  /exit, /quit           - завершить работу"""


def estimate_history_tokens(history: list, hm: HistoryManager) -> int:
    hm.load_messages(history)
    return hm.estimate_tokens()


def handle_command(
    cmd_line: str,
    history: list,
    source_uuid: str,
    ctx_store: ContextStore,
    cache: ResponseCache,
    logger: SessionLogger,
    hm: HistoryManager,
) -> Tuple[str, list]:
    parts = cmd_line.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    if cmd in ("/exit", "/quit", "exit", "quit"):
        return "exit", history
    if cmd == "/help":
        print(f"\n{HELP_TEXT}")
        return "continue", history
    if cmd == "/uuid":
        print(f"\nsource_uuid: {source_uuid}")
        return "continue", history
    if cmd == "/paths":
        print(
            f"\nКонтекст: {ctx_store.context_path}"
            f"\nЖурнал:   {logger.log_path}"
            f"\nКеш:      {cache.cache_path}"
        )
        return "continue", history
    if cmd == "/context":
        tokens = estimate_history_tokens(history, hm)
        print(f"\nСообщений в контексте: {len(history)} (~{tokens} токенов)")
        return "continue", history
    if cmd == "/compact":
        hm.load_messages(history)
        stats = hm.compact_in_memory()
        print(
            f"\nСжатие в памяти: {stats['before_tokens']} -> {stats['after_tokens']} токенов "
            f"(осталось сообщений: {stats['messages_left']})"
        )
        return "continue", list(hm.messages)
    if cmd == "/reset":
        ctx_store.clear()
        hm.load_messages([])
        logger.log("context_reset")
        print("\nКонтекст диалога очищен.")
        return "continue", []
    if cmd == "/cache":
        sub = arg.lower()
        if sub == "on":
            cache.enabled = True
            print("\nКеш ответов включён.")
        elif sub == "off":
            cache.enabled = False
            print("\nКеш ответов выключен.")
        elif sub == "clear":
            removed = cache.clear()
            print(f"\nКеш очищен (удалено записей: {removed}).")
        else:
            state = "включён" if cache.enabled else "выключен"
            print(f"\nКеш: {state} | попаданий: {cache.hits}, промахов: {cache.misses}")
        return "continue", history
    if cmd == "/save":
        if not arg:
            print("\nУкажите путь: /save session.json")
            return "continue", history
        hm.load_messages(history)
        saved = hm.save_to_disk(Path(arg).expanduser())
        print(f"\nКонтекст экспортирован в {saved}")
        return "continue", history
    if cmd == "/load":
        if not arg:
            print("\nУкажите путь: /load session.json")
            return "continue", history
        path = Path(arg).expanduser()
        if not path.is_file():
            print(f"\nФайл не найден: {path}")
            return "continue", history
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, list):
            print("\nНекорректный формат файла истории: ожидался JSON-список.")
            return "continue", history
        ctx_store.save(loaded)
        hm.load_messages(loaded)
        print(f"\nЗагружено сообщений из {path}: {len(loaded)}")
        return "continue", loaded

    print("\nНеизвестная команда. Введите /help для списка команд.")
    return "continue", history