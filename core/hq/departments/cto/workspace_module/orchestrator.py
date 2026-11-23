"""Оркестратор запуска инфраструктуры рабочего пространства."""

import logging
from typing import Any, Dict, Optional

from workspace_module.initializer import init_system

logger = logging.getLogger(__name__)


class _FallbackTracker:
    def log_status(self, stage: str, state: str, detail: str = "") -> None:
        msg = f"[{stage}] {state}" + (f": {detail}" if detail else "")
        logger.info(msg)


class Orchestrator:
    """Координирует инициализацию и запуск циклов рабочего пространства."""

    def __init__(self, status_logger: Optional[Any] = None) -> None:
        self.tracker = status_logger if status_logger is not None else _FallbackTracker()

    def start_cycle(self, import_check: bool = False) -> bool:
        """Инициализирует инфраструктуру через реестр."""
        self.tracker.log_status("ORCHESTRATOR", "starting_system")
        init_result = init_system(status_logger=self.tracker, import_check=import_check)
        if init_result.get("status") == "initialized":
            self.tracker.log_status("ORCHESTRATOR", "system_ready")
            return True
        self.tracker.log_status("ORCHESTRATOR", "init_failed")
        return False

    def run_night_mode(self, task_label: str = "night_cycle") -> Dict[str, Any]:
        """Подготавливает инфраструктуру для автономного прогона и возвращает сводку."""
        self.tracker.log_status("ORCHESTRATOR", "night_mode_start", task_label)
        ok = self.start_cycle(import_check=False)
        state = "night_mode_ready" if ok else "night_mode_failed"
        self.tracker.log_status("ORCHESTRATOR", state, task_label)
        return {"ok": ok, "task": task_label}