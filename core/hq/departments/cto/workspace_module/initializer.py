"""Инициализация модулей рабочего пространства через SystemRegistry."""

import importlib
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from workspace_module.system_registry import SystemRegistry

logger = logging.getLogger(__name__)


class _FallbackStatusLogger:
    """Резервный логгер статуса, если внешний трекер не передан."""

    def log_status(self, stage: str, state: str, detail: str = "") -> None:
        msg = f"[{stage}] {state}" + (f": {detail}" if detail else "")
        logger.info(msg)


def _load_fs_wrapper() -> Any:
    try:
        mod = importlib.import_module("workspace_module.fs_wrapper")
        cls = getattr(mod, "FSWrapper", None)
        return cls() if callable(cls) else None
    except Exception as exc:
        logger.debug("FSWrapper недоступен при инициализации: %s", exc)
        return None


class SystemInitializer:
    """Инициализация компонентов системы согласно реестру."""

    def __init__(
        self,
        registry: Optional[SystemRegistry] = None,
        status_logger: Optional[Any] = None,
        module_dir: Optional[Path] = None,
    ) -> None:
        self.registry = registry or SystemRegistry(module_dir=module_dir)
        self.tracker = status_logger if status_logger is not None else _FallbackStatusLogger()
        self.fs = _load_fs_wrapper()

    def bootstrap(self, import_check: bool = False) -> Dict[str, Any]:
        """Проверяет реестр модулей и фиксирует состояние инициализации."""
        modules = self.registry.get_modules()
        status = self.registry.resolve_existing()
        imported: list[str] = []
        import_errors: Dict[str, str] = {}

        if import_check:
            for mod_name in status["present"]:
                if mod_name in {"initializer", "main_gatekeeper"}:
                    imported.append(mod_name)
                    continue
                try:
                    importlib.import_module(f"workspace_module.{mod_name}")
                    imported.append(mod_name)
                except Exception as exc:
                    import_errors[mod_name] = str(exc)

        detail = (
            f"present={len(status['present'])}, missing={len(status['missing'])}, "
            f"import_errors={len(import_errors)}"
        )
        self.tracker.log_status("SYSTEM_BOOTSTRAP", "completed", detail)
        return {
            "status": "initialized",
            "modules": modules,
            "present": status["present"],
            "missing": status["missing"],
            "imported": imported,
            "import_errors": import_errors,
            "fs_ready": self.fs is not None,
        }


def init_system(
    status_logger: Optional[Any] = None,
    import_check: bool = False,
) -> Dict[str, Any]:
    """Точка входа для инициализации рабочего пространства."""
    initializer = SystemInitializer(status_logger=status_logger)
    return initializer.bootstrap(import_check=import_check)