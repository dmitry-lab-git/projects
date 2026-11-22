"""Файловые инструменты агента: только чтение, только внутри разрешённого периметра.

Граница проверяется по реальному пути (resolve раскрывает симлинки и '../').
Это вторая линия обороны: основная граница задаётся правами ОС / песочницей.
"""
import os
from pathlib import Path

_DEFAULT_ROOTS = (
    "/home/fujitsu-u745/Projects/core/hq/departments/cto",
    "/home/fujitsu-u745/Projects/core/api_manager",
)
# CTO_AGENT_ROOTS читает только процесс-хозяин (для тестов); агент окружение не меняет.
ROOTS = [
    Path(p).resolve()
    for p in os.environ.get("CTO_AGENT_ROOTS", ":".join(_DEFAULT_ROOTS)).split(":")
    if p
]

DENY_NAMES = {"vault.yaml", "credentials.conf", ".pgpass"}
DENY_PREFIXES = (".env",)
DENY_SUFFIXES = (".pem", ".key")
DENY_PARTS = {"secure_folder", ".git"}

MAX_BYTES = 100_000
MAX_LIST = 500


def _safe(path: str) -> Path:
    raw = Path(path).expanduser()
    if not raw.is_absolute():
        raw = ROOTS[0] / raw          # относительные пути считаем от первого корня
    p = raw.resolve()
    if not any(p == r or p.is_relative_to(r) for r in ROOTS):
        raise PermissionError("Путь вне разрешённого периметра")
    if (p.name in DENY_NAMES
            or p.name.startswith(DENY_PREFIXES)
            or p.name.endswith(DENY_SUFFIXES)
            or DENY_PARTS.intersection(p.parts)):
        raise PermissionError("Доступ к этому файлу запрещён")
    return p


def list_dir(path: str = ".") -> dict:
    """Список файлов и папок в каталоге."""
    try:
        p = _safe(path)
        if not p.is_dir():
            return {"ok": False, "error": "Это не каталог"}
        items = [{"name": c.name, "dir": c.is_dir()} for c in sorted(p.iterdir())]
        return {"ok": True, "items": items[:MAX_LIST], "truncated": len(items) > MAX_LIST}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def read_file(path: str) -> dict:
    """Прочитать текстовый файл (до 100 КБ)."""
    try:
        p = _safe(path)
        if not p.is_file():
            return {"ok": False, "error": "Это не файл"}
        size = p.stat().st_size
        with p.open("rb") as f:
            data = f.read(MAX_BYTES)
        if b"\0" in data:
            return {"ok": False, "error": "Бинарный файл не читается"}
        return {"ok": True, "text": data.decode("utf-8", errors="replace"),
                "truncated": size > MAX_BYTES}
    except Exception as e:
        return {"ok": False, "error": str(e)}
        
def write_file(path: str, content: str) -> dict:
    """Записать текст в файл (до 100 КБ)."""
    try:
        p = _safe(path)
        # Проверка размера контента
        if len(content.encode('utf-8')) > MAX_BYTES:
            return {"ok": False, "error": f"Размер превышает лимит {MAX_BYTES} байт"}
        
        with p.open("w", encoding="utf-8") as f:
            f.write(content)
        return {"ok": True, "message": f"Файл {p.name} успешно записан"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# Реестр: имя -> (функция, описание для модели)
TOOLS = {
    "list_dir": (list_dir, 'list_dir(path) - список содержимого каталога. Пример args: {"path": "."}'),
    "read_file": (read_file, 'read_file(path) - прочитать текстовый файл. Пример args: {"path": "agent_runner.py"}'),
    "write_file": (write_file, 'write_file(path, content) - записать текст в файл. Пример args: {"path": "test.txt", "content": "..."}'),
}

