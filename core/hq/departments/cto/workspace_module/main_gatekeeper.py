"""Главный контроллер жизненного цикла рабочего пространства."""

import logging
from typing import Any, Dict, Optional

from workspace_module.initializer import SystemInitializer

logger = logging.getLogger(__name__)


def _optional_instance(module_path: str, class_name: str) -> Optional[Any]:
    try:
        mod = __import__(module_path, fromlist=[class_name])
        cls = getattr(mod, class_name, None)
        return cls() if callable(cls) else None
    except Exception as exc:
        logger.debug("Модуль %s.%s пока не подключён: %s", module_path, class_name, exc)
        return None


class MainGatekeeper:
    """Координатор инициализации, очистки и проверки состояния модулей."""

    def __init__(
        self,
        initializer: Optional[SystemInitializer] = None,
        audit_tool: Optional[Any] = None,
        emergency_cleanup: Optional[Any] = None,
    ) -> None:
        self.init = initializer or SystemInitializer()
        self.audit = audit_tool if audit_tool is not None else _optional_instance(
            "workspace_module.audit_tool", "AuditTool"
        )
        self.clean = emergency_cleanup if emergency_cleanup is not None else _optional_instance(
            "workspace_module.emergency_cleanup", "EmergencyCleanup"
        )

    def run_health_check(self) -> Dict[str, Any]:
        """Запускает аудит при наличии AuditTool."""
        if self.audit is None or not hasattr(self.audit, "run_report"):
            return {"status": "ok", "violations": [], "audit_skipped": True}
        violations = self.audit.run_report()
        if violations:
            return {"status": "warning", "violations": violations}
        return {"status": "ok", "violations": []}

    def run_cleanup(self) -> Dict[str, Any]:
        """Очищает временные файлы при наличии EmergencyCleanup."""
        if self.clean is None or not hasattr(self.clean, "cleanup_temp_files"):
            return {"status": "skipped"}
        res = self.clean.cleanup_temp_files()
        return res if isinstance(res, dict) else {"status": "ok", "result": res}

    def full_cycle_maintenance(self, import_check: bool = False) -> Dict[str, Any]:
        """Порядок: очистка -> инициализация реестра -> проверка состояния."""
        cleanup_res = self.run_cleanup()
        bootstrap_res = self.init.bootstrap(import_check=import_check)
        health_res = self.run_health_check()
        return {
            "status": health_res["status"],
            "cleanup": cleanup_res,
            "bootstrap": bootstrap_res,
            "health": health_res,
        }