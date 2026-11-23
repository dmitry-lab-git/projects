"""Реестр модулей рабочего пространства технического департамента."""

from pathlib import Path
from typing import Dict, List


class SystemRegistry:
    """Реестр модулей системы с проверкой их наличия в каталоге модуля."""

    DEFAULT_MODULES: List[str] = [
        "code_autonomy",
        "orchestrator",
        "fs_wrapper",
        "history_compressor",
        "history_manager",
        "audit_tool",
        "initializer",
        "main_gatekeeper",
        "emergency_cleanup",
        "integrity_check",
        "heartbeat",
        "run_test",
    ]

    def __init__(self, module_dir: Path | None = None, modules: List[str] | None = None) -> None:
        self.module_dir = (module_dir or Path(__file__).resolve().parent).resolve()
        source = modules if modules is not None else self.DEFAULT_MODULES
        self._modules: List[str] = []
        for name in source:
            self.register_module(name)

    def get_modules(self) -> List[str]:
        """Возвращает копию списка зарегистрированных модулей."""
        return list(self._modules)

    def register_module(self, name: str) -> bool:
        """Регистрирует имя модуля без дублей и некорректных символов."""
        clean = name.strip()
        if not clean or not clean.replace("_", "").isalnum():
            raise ValueError(f"Некорректное имя модуля: {name!r}")
        if clean not in self._modules:
            self._modules.append(clean)
            return True
        return False

    def resolve_existing(self) -> Dict[str, List[str]]:
        """Разделяет зарегистрированные модули на присутствующие на диске и отсутствующие."""
        present: List[str] = []
        missing: List[str] = []
        for name in self._modules:
            py_file = self.module_dir / f"{name}.py"
            pkg_init = self.module_dir / name / "__init__.py"
            if py_file.is_file() or pkg_init.is_file():
                present.append(name)
            else:
                missing.append(name)
        return {"present": present, "missing": missing}