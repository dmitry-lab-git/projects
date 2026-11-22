"""Цикл выполнения хода агента, сжатие на 15k токенов и ночной автономный режим."""
import json
import logging
import time
from typing import Callable, Optional

from agent_runner import run_agent
from session_store import ContextStore, ResponseCache, SessionLogger
from workspace_module.chat.commands import handle_command
from workspace_module.chat.history_manager import HistoryManager

STATUS_TEXT = {
    "model_error": (
        "Модель не ответила (проверьте сеть/DNS, --source-uuid и target_name; "
        "подробности смотрите в traceback выше). Контекст этого хода откачен."
    ),
    "max_steps": "Достигнут лимит шагов. Контекст этого хода откачен.",
    "loop": "Агент зациклился на одном вызове и был остановлен. Контекст этого хода откачен.",
    "cancelled": "Текущий ход отменён. Контекст этого хода откачен.",
}


def make_event_handler(logger: SessionLogger) -> Callable[[dict], None]:
    def _show(ev: dict) -> None:
        logger.log(ev["type"], **{k: v for k, v in ev.items() if k != "type"})
        if ev["type"] == "tool_call":
            print(f"  -> {ev['tool']}({json.dumps(ev['args'], ensure_ascii=False)})")
        elif ev["type"] == "tool_result":
            print(f"  <- {ev['tool']}: {'ok' if ev['ok'] else 'ошибка'}")
    return _show


def ask_interactive(question: str) -> Optional[str]:
    print(f"\n[Агент спрашивает] {question}")
    try:
        return input("Ваш ответ: ")
    except EOFError:
        return None
    except KeyboardInterrupt:
        print("\n(ввод ответа отменён)")
        return None


def ask_overnight(question: str) -> str:
    logging.warning("Ночной режим: автоответ на вопрос агента (%s)", question)
    return (
        "Автономный ночной режим без оператора: выбери самый безопасный и модульный "
        "вариант в рамках правил (лимит 200 строк на файл, ROOTS, сжатие истории на 15k "
        "токенов без потери сути задачи) и продолжай работу."
    )


def sanitize_text(text: str) -> str:
    return text.encode("utf-8", errors="replace").decode("utf-8")


def compact_if_needed(hm: HistoryManager, history: list) -> list:
    hm.load_messages(history)
    if hm.estimate_tokens() >= hm.token_threshold:
        stats = hm.compact_in_memory()
        logging.info(
            "Сжатие истории: %s -> %s токенов (сообщений: %s)",
            stats["before_tokens"],
            stats["after_tokens"],
            stats["messages_left"],
        )
    return list(hm.messages)


def run_overnight_loop(
    question: Optional[str],
    call: Callable[[str], Optional[str]],
    history: list,
    hm: HistoryManager,
    ctx_store: ContextStore,
    logger: SessionLogger,
    on_event: Callable[[dict], None],
    max_cycles: int,
    step_limit: int,
    sleep_on_error: float,
) -> None:
    base_task = (question or "").strip() or (
        "Продолжай автономно развивать инфраструктуру технического департамента "
        "в workspace_module/ (лимит 200 строк на файл, сжатие на 15k токенов)."
    )
    for cycle in range(1, max_cycles + 1):
        history = compact_if_needed(hm, history)
        prompt = base_task if cycle == 1 else (
            f"Ночной цикл #{cycle}/{max_cycles}. Продолжай работу без вопросов "
            "пользователю, соблюдай лимит до 200 строк на файл и сохраняй суть задачи."
        )
        logger.log("overnight_cycle_start", cycle=cycle)
        try:
            out = run_agent(
                prompt, call, history=history, on_event=on_event,
                max_steps=step_limit, ask_user=ask_overnight,
            )
        except KeyboardInterrupt:
            print("\nНочной цикл остановлен пользователем.")
            break
        except Exception as exc:
            logging.exception("Сбой на цикле #%s: %s", cycle, exc)
            logger.log("exception", cycle=cycle, error=str(exc))
            time.sleep(sleep_on_error)
            continue

        if out["status"] == "ok":
            history = compact_if_needed(hm, out["history"])
            ctx_store.save(history)
            logger.log("assistant_answer", cycle=cycle, answer=out["answer"], steps=len(out["steps"]))
            print(f"\n[Цикл {cycle}] Агент: {out['answer']}")
        else:
            history = compact_if_needed(hm, out.get("rollback_history", history))
            logger.log("turn_aborted", cycle=cycle, status=out["status"])
            print(f"\n[Цикл {cycle}] {STATUS_TEXT.get(out['status'], 'Ход прерван.')}")
            if out["status"] in ("model_error", "loop"):
                time.sleep(sleep_on_error)


def run_chat_loop(
    initial_question: Optional[str],
    call: Callable[[str], Optional[str]],
    history: list,
    source_uuid: str,
    hm: HistoryManager,
    ctx_store: ContextStore,
    cache: ResponseCache,
    logger: SessionLogger,
    on_event: Callable[[dict], None],
    step_limit: int,
) -> None:
    one_shot = initial_question is not None
    pending_question = initial_question
    consecutive_interrupts = 0

    while True:
        if pending_question is None:
            try:
                raw = input("\nВы: ")
                text = sanitize_text(raw).strip()
                consecutive_interrupts = 0
            except EOFError:
                print("\nЗавершение сессии (EOF).")
                break
            except KeyboardInterrupt:
                consecutive_interrupts += 1
                if consecutive_interrupts >= 2:
                    print("\nПовторный Ctrl+C — выход из чата.")
                    break
                print("\nНажмите Ctrl+C ещё раз или введите /exit для выхода из чата.")
                continue
            if not text:
                continue
            if text.startswith("/") or text.lower() in ("exit", "quit"):
                action, history = handle_command(
                    text, history, source_uuid, ctx_store, cache, logger, hm
                )
                if action == "exit":
                    break
                continue
            question = text
        else:
            question = sanitize_text(pending_question).strip()
            pending_question = None
            if not question:
                if one_shot:
                    break
                continue

        history = compact_if_needed(hm, history)
        logger.log("user_question", question=question)
        try:
            out = run_agent(
                question, call, history=history, on_event=on_event,
                max_steps=step_limit, ask_user=ask_interactive,
            )
        except Exception as exc:
            logging.exception("Ошибка во время выполнения хода агента: %s", exc)
            logger.log("exception", error=str(exc))
            print(f"\n[error] Сбой при выполнении хода: {exc}. Контекст этого хода откачен.")
            if one_shot:
                break
            continue

        if out["status"] == "ok":
            history = compact_if_needed(hm, out["history"])
            ctx_store.save(history)
            logger.log("assistant_answer", answer=out["answer"], steps=len(out["steps"]))
            print(f"\nАгент: {out['answer']}")
        else:
            history = compact_if_needed(hm, out.get("rollback_history", history))
            logger.log("turn_aborted", status=out["status"])
            print(f"\n[{out['status']}] {STATUS_TEXT.get(out['status'], 'Ход прерван.')}")

        if one_shot:
            break