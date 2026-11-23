"""Проверка доступности и импортируемости ключевых модулей."""

import importlib
import sys
from typing import Dict, List

MODULES_TO_CHECK: List[str] = [
    "session_store",
    "workspace_module.chat.commands",
    "workspace_module.chat.history_manager",
    "workspace_module.orchestrator",
    "workspace_module.main_gatekeeper",
]


def verify_imports(modules: List[str] | None = None) -> Dict[str, object]:
    """Проверяет импорт всех указанных модулей без остановки на первой ошибке."""
    targets = modules if modules is not None else MODULES_TO_CHECK
    ok_modules: List[str] = []
    failed: Dict[str, str] = {}

    for mod_name in targets:
        try:
            importlib.import_module(mod_name)
            ok_modules.append(mod_name)
        except Exception as exc:
            failed[mod_name] = str(exc)

    return {
        "ok": len(failed) == 0,
        "checked": len(targets),
        "ok_modules": ok_modules,
        "failed": failed,
    }


def main() -> int:
    report = verify_imports()
    print("--- Проверка импортов ---")
    for name in report["ok_modules"]:
        print(f"OK: {name}")
    for name, err in report["failed"].items():
        print(f"FAIL: {name} - {err}")

    if report["ok"]:
        print("Все модули доступны.")
        return 0
    print(f"Ошибок импорта: {len(report['failed'])}")
    return 1


if __name__ == "__main__":
    sys.exit(main())