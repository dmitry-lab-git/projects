"""Проверка синтаксиса .py файлов перед записью в разрешённом периметре."""

import ast
import importlib
import logging
from typing import Any, Dict, Optional

from fs_tools import write_file as fs_write_file

logger = logging.getLogger(__name__)


def _load_safe_file_io() -> Optional[Any]:
    try:
        mod = importlib.import_module("workspace_module.io.file_ops")
        cls = getattr(mod, "SafeFileIO", None)
        return cls() if callable(cls) else None
    except Exception:
        return None


class CodeAutonomy:
    """Валидирует Python-код через AST и записывает через безопасный слой."""

    def __init__(self, io_handler: Optional[Any] = None) -> None:
        self.io = io_handler if io_handler is not None else _load_safe_file_io()

    def apply_fix(self, file_path: str, new_content: str) -> Dict[str, Any]:
        """Проверяет синтаксис (для .py) и записывает файл."""
        if file_path.endswith(".py"):
            try:
                ast.parse(new_content)
            except SyntaxError as exc:
                msg = f"Ошибка синтаксиса в {file_path}: {exc}"
                logger.warning(msg)
                return {"ok": False, "error": msg}

        try:
            if self.io is not None and hasattr(self.io, "write"):
                self.io.write(file_path, new_content)
                return {"ok": True, "path": file_path}
            res = fs_write_file(file_path, new_content)
            return res if isinstance(res, dict) else {"ok": bool(res), "path": file_path}
        except Exception as exc:
            msg = f"Ошибка записи {file_path}: {exc}"
            logger.exception(msg)
            return {"ok": False, "error": msg}