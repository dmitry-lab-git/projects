from pathlib import Path
from typing import List
from workspace_module.io.file_ops import SafeFileIO

class HistoryManager:
    """Управление историей с FIFO стратегией и лимитом токенов."""

    def __init__(self, io: SafeFileIO, history_dir: str = "history", max_tokens: int = 15000) -> None:
        self.io = io
        self.history_dir = Path(history_dir)
        self.max_tokens = max_tokens

    def _get_history_files(self) -> List[Path]:
        items = self.io.list_dir(self.history_dir)
        return sorted([self.history_dir / f for f in items if not f.endswith("/")])

    def append_record(self, content: str) -> None:
        """Добавляет запись и проверяет лимит токенов (грубая оценка: 1 символ ~ 0.75 токена)."""
        files = self._get_history_files()
        new_file = self.history_dir / f"log_{len(files)}.txt"
        self.io.write_text(new_file, content)
        
        self._rotate_if_needed()

    def _rotate_if_needed(self) -> None:
        files = self._get_history_files()
        total_content = "".join(self.io.read_text(f) for f in files)
        
        if len(total_content) > self.max_tokens * 1.2:
            # Удаление самого старого файла при превышении лимита
            oldest = files[0]
            oldest.unlink()
