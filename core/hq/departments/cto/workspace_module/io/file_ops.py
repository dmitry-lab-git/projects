from pathlib import Path
from typing import List
from workspace_module.security.path_guard import PathGuard


class SafeFileIO:
    """Безопасное чтение, запись и листинг в пределах PathGuard."""

    def __init__(self, guard: PathGuard) -> None:
        self.guard = guard

    def list_dir(self, path: str | Path = ".") -> List[str]:
        target = self.guard.resolve_safe(path, allow_protected=True)
        if not target.exists() or not target.is_dir():
            raise FileNotFoundError(f"Каталог не найден: {target}")
        return sorted(p.name + ("/" if p.is_dir() else "") for p in target.iterdir())

    def read_text(self, path: str | Path, encoding: str = "utf-8") -> str:
        target = self.guard.resolve_safe(path, allow_protected=True)
        return target.read_text(encoding=encoding)

    def write_text(
        self, path: str | Path, content: str, overwrite: bool = True, encoding: str = "utf-8"
    ) -> Path:
        target = self.guard.resolve_safe(path, allow_protected=False)
        if target.exists() and not overwrite:
            raise FileExistsError(f"Файл уже существует и перезапись запрещена: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding=encoding)
        return target