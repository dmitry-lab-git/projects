"""Очистка кэшей и временных файлов рабочего пространства."""

from pathlib import Path
import shutil
from typing import Dict, List


class EmergencyCleanup:
    """Модуль безопасной очистки временных артефактов без удаления рабочих скриптов."""

    def __init__(self, workspace: str | Path = "workspace_module") -> None:
        self.workspace = Path(workspace).resolve()

    def cleanup_temp_files(self) -> Dict[str, object]:
        """Удаляет __pycache__ и временные файлы (*.tmp, *.bak, test_sandbox.txt)."""
        removed_dirs: List[str] = []
        removed_files: List[str] = []

        if not self.workspace.exists() or not self.workspace.is_dir():
            return {"ok": False, "error": "Каталог рабочего пространства не найден"}

        for pycache in self.workspace.rglob("__pycache__"):
            if pycache.is_dir():
                shutil.rmtree(pycache, ignore_errors=True)
                removed_dirs.append(str(pycache))

        temp_names = {"test_sandbox.txt"}
        temp_suffixes = (".tmp", ".bak")
        for item in self.workspace.rglob("*"):
            if item.is_file() and (item.name in temp_names or item.suffix in temp_suffixes):
                item.unlink(missing_ok=True)
                removed_files.append(str(item))

        return {
            "ok": True,
            "removed_dirs": removed_dirs,
            "removed_files": removed_files,
        }