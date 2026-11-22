import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


class HistoryManager:
    """Управление историей: сжатие на 15k токенов, архив на диске и сохранение по команде."""

    def __init__(
        self,
        archive_path: str | Path = ".cto_agent/history_archive.jsonl",
        llm_manifest_path: str | Path = "llm.txt",
        token_threshold: int = 15_000,
        keep_recent: int = 6,
        chars_per_token: int = 4,
        max_summary_items: int = 20,
        max_entry_chars: int = 180,
    ) -> None:
        self.archive_path = Path(archive_path)
        self.llm_manifest_path = Path(llm_manifest_path)
        self.token_threshold = token_threshold
        self.keep_recent = max(1, keep_recent)
        self.chars_per_token = max(1, chars_per_token)
        self.max_summary_items = max(5, max_summary_items)
        self.max_entry_chars = max(40, max_entry_chars)
        self.messages: List[Dict[str, str]] = []
        self.compactions_count: int = 0

    def load_messages(self, messages: List[Dict[str, str]]) -> None:
        self.messages = [
            {"role": str(m.get("role", "user")), "content": str(m.get("content", ""))}
            for m in messages
        ]

    def estimate_tokens(self, messages: List[Dict[str, str]] | None = None) -> int:
        target = messages if messages is not None else self.messages
        total_chars = sum(
            len(m.get("role", "")) + len(m.get("content", "")) + 16 for m in target
        )
        return total_chars // self.chars_per_token

    def append_to_archive(self, role: str, content: str) -> None:
        """Дописывает запись в долговременный архив на диске."""
        self.archive_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "content": content,
        }
        with self.archive_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def add_message(
        self,
        role: str,
        content: str,
        auto_compact: bool = True,
        archive: bool = False,
    ) -> List[Dict[str, str]]:
        self.messages.append({"role": role, "content": content})
        if archive:
            self.append_to_archive(role, content)
        if auto_compact and self.estimate_tokens() >= self.token_threshold:
            self.compact_in_memory()
        return self.messages

    def _format_snippet(self, message: Dict[str, str]) -> str:
        role = message.get("role", "user")
        text = " ".join(message.get("content", "").strip().split())
        if len(text) > self.max_entry_chars:
            text = text[: self.max_entry_chars].rstrip() + "..."
        return f"- [{role}] {text}"

    def _read_manifest_anchor(self) -> str:
        if self.llm_manifest_path.is_file():
            return self.llm_manifest_path.read_text(encoding="utf-8").strip()
        return (
            "Якорь задачи: автономное развитие инфраструктуры технического департамента "
            "в workspace_module/ (лимит 200 строк на файл, защита ROOTS, сжатие на 15k токенов)."
        )

    def compact_in_memory(self) -> Dict[str, int]:
        """Сжимает старые сообщения в памяти с сохранением сути задачи без записи на диск."""
        before_tokens = self.estimate_tokens()
        if len(self.messages) <= self.keep_recent:
            return {
                "before_tokens": before_tokens,
                "after_tokens": before_tokens,
                "messages_left": len(self.messages),
            }

        older = self.messages[: -self.keep_recent]
        recent = self.messages[-self.keep_recent :]

        snippets: List[str] = []
        for item in older:
            content = item.get("content", "")
            if item.get("role") == "system" and "Сжатая сводка истории" in content:
                lines = [
                    line.strip()
                    for line in content.splitlines()
                    if line.strip().startswith("- ")
                ]
                snippets.extend(lines)
            else:
                snippets.append(self._format_snippet(item))

        trimmed_snippets = snippets[-self.max_summary_items :]
        summary_body = "\n".join(trimmed_snippets)
        anchor = self._read_manifest_anchor()
        summary_msg = {
            "role": "system",
            "content": (
                f"{anchor}\n\n"
                f"Сжатая сводка истории (этап #{self.compactions_count + 1}, "
                f"архив: {self.archive_path}):\n{summary_body}"
            ),
        }

        self.messages = [summary_msg, *recent]
        self.compactions_count += 1
        after_tokens = self.estimate_tokens()
        return {
            "before_tokens": before_tokens,
            "after_tokens": after_tokens,
            "messages_left": len(self.messages),
        }

    def clear_history(self, keep_system_anchor: bool = True) -> Dict[str, int]:
        """Очищает историю в памяти (опционально сохраняя системный якорь)."""
        before_tokens = self.estimate_tokens()
        if keep_system_anchor and self.messages and self.messages[0].get("role") == "system":
            self.messages = [self.messages[0]]
        else:
            self.messages = []
        after_tokens = self.estimate_tokens()
        return {
            "before_tokens": before_tokens,
            "after_tokens": after_tokens,
            "messages_left": len(self.messages),
        }

    def save_to_disk(self, target_path: str | Path, encoding: str = "utf-8") -> Path:
        """Сохраняет текущую историю на диск только при явном вызове."""
        path = Path(target_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.messages, ensure_ascii=False, indent=2), encoding=encoding
        )
        return path