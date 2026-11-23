"""Обёртка над записью файлов с проверкой через Orchestrator."""

from typing import Any, Dict, Optional

from fs_tools import write_file as original_write
from workspace_module.orchestrator import Orchestrator


class FSWrapper:
    """Выполняет предпроверку/подготовку через Orchestrator и пишет через fs_tools."""

    def __init__(self, orchestrator: Optional[Orchestrator] = None) -> None:
        self.orchestrator = orchestrator or Orchestrator()

    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        if hasattr(self.orchestrator, "validate_before_write"):
            check = self.orchestrator.validate_before_write(path, content)
            if isinstance(check, dict) and not check.get("ok", True):
                return check
            if check is False:
                return {"ok": False, "error": "Проверка перед записью не пройдена"}
        elif hasattr(self.orchestrator, "save_file"):
            # Если оркестратор сам сохраняет/проверяет, не дублируем запись без необходимости
            saved = self.orchestrator.save_file(path, content)
            if not saved:
                return {"ok": False, "error": "Оркестратор отклонил запись файла"}
            return {"ok": True, "message": f"Файл {path} обработан через Orchestrator"}

        return original_write(path, content)