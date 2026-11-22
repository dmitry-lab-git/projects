from typing import Any, Callable, Dict
from workspace_module.chat.history_manager import HistoryManager
from workspace_module.io.file_ops import SafeFileIO


class ChatSession:
    """Цикл чата с контролем размера истории (15k токенов) и диспетчеризацией."""

    def __init__(
        self,
        file_io: SafeFileIO,
        history: HistoryManager,
        reply_fn: Callable[[list[Dict[str, str]]], str],
    ) -> None:
        self.file_io = file_io
        self.history = history
        self.reply_fn = reply_fn

    def step(self, user_input: str, save_path: str | None = None) -> Dict[str, Any]:
        cmd = user_input.strip()
        if cmd.startswith("/save"):
            parts = cmd.split(maxsplit=1)
            dest = parts[1].strip() if len(parts) > 1 and parts[1].strip() else (save_path or "")
            if not dest:
                return {"status": "error", "message": "Укажите путь для сохранения: /save путь/к/файлу.json"}
            safe_dest = self.file_io.guard.resolve_safe(dest, allow_protected=False)
            saved = self.history.save_to_disk(safe_dest)
            return {"status": "saved", "path": str(saved), "tokens": self.history.estimate_tokens()}

        if cmd == "/compact":
            self.history.compact_in_memory()
            return {"status": "compacted", "tokens": self.history.estimate_tokens()}

        self.history.add_message("user", user_input, auto_compact=True)
        assistant_reply = self.reply_fn(self.history.messages)
        self.history.add_message("assistant", assistant_reply, auto_compact=True)
        return {
            "status": "ok",
            "reply": assistant_reply,
            "tokens": self.history.estimate_tokens(),
            "messages_count": len(self.history.messages),
        }