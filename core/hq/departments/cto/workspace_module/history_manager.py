"""Локальный файловый журнал записей истории для workspace_module."""

from pathlib import Path
from typing import List


class HistoryManager:
    """Хранит записи истории в каталоге и ротирует старые при превышении лимита токенов."""

    def __init__(
        self,
        history_dir: str | Path = "history",
        max_tokens: int = 15_000,
        chars_per_token: int = 4,
    ) -> None:
        self.history_dir = Path(history_dir)
        self.max_tokens = max(100, int(max_tokens))
        self.chars_per_token = max(1, int(chars_per_token))
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self._seq = self._detect_next_index()

    def _detect_next_index(self) -> int:
        existing = list(self.history_dir.glob("log_*.txt"))
        return len(existing)

    def _estimate_dir_tokens(self, files: List[Path]) -> int:
        total_chars = 0
        for item in files:
            if item.is_file():
                total_chars += len(item.read_text(encoding="utf-8"))
        return total_chars // self.chars_per_token

    def append_record(self, content: str) -> Path:
        """Добавляет запись в историю и удаляет самые старые файлы при превышении порога."""
        target = self.history_dir / f"log_{self._seq}.txt"
        self._seq += 1
        target.write_text(content, encoding="utf-8")

        files = sorted(
            [p for p in self.history_dir.glob("log_*.txt") if p.is_file()],
            key=lambda p: p.stat().st_mtime,
        )
        while len(files) > 1 and self._estimate_dir_tokens(files) > self.max_tokens:
            oldest = files.pop(0)
            oldest.unlink(missing_ok=True)

        return target