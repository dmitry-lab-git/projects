from pathlib import Path
from typing import Iterable, List


class SecurityError(PermissionError):
    """Нарушение политики безопасности файловой системы."""


class PathGuard:
    """Проверка путей относительно разрешённых корней и защищённых целей."""

    def __init__(self, roots: Iterable[Path], protected_names: Iterable[str] | None = None) -> None:
        self.roots: List[Path] = [Path(r).resolve() for r in roots]
        self.protected_names = set(
            protected_names
            or {"agent_runner.py", "fs_tools.py", "context.json", "settings.txt"}
        )

    def resolve_safe(self, target: str | Path, allow_protected: bool = False) -> Path:
        resolved = Path(target).resolve()
        if not any(resolved == root or root in resolved.parents for root in self.roots):
            raise SecurityError(f"Путь вне разрешённых границ ROOTS: {resolved}")
        if not allow_protected and (
            resolved.name in self.protected_names or ".cto_agent" in resolved.parts
        ):
            raise SecurityError(f"Запрещён доступ к защищённому файлу: {resolved}")
        return resolved