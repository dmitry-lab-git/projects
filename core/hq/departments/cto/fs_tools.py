"""Файловые и ограниченные shell-инструменты агента внутри разрешённого периметра.

Граница проверяется по реальному пути (resolve раскрывает симлинки и '../').
Это вторая линия обороны: основная граница задаётся правами ОС / песочницей.
"""
import os
import shlex
import subprocess
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

ALLOWED_BINS = {
    "python", "python3", "pytest", "unittest", "git",
    "ls", "cat", "head", "tail", "wc", "grep", "rg", "find", "tree", "diff",
    "ruff", "flake8", "mypy", "ps", "free",
}

MAX_BYTES = 100_000
MAX_LIST = 500
SHELL_TIMEOUT_SEC = 30
MAX_STREAM_CHARS = 12_000


def _safe(path: str) -> Path:
    raw = Path(path).expanduser()
    if not raw.is_absolute():
        raw = ROOTS[0] / raw  # относительные пути считаем от первого корня
    p = raw.resolve()
    if not any(p == r or p.is_relative_to(r) for r in ROOTS):
        raise PermissionError("Путь вне разрешённого периметра")
    if (
        p.name in DENY_NAMES
        or p.name.startswith(DENY_PREFIXES)
        or p.name.endswith(DENY_SUFFIXES)
        or DENY_PARTS.intersection(p.parts)
    ):
        raise PermissionError("Доступ к этому файлу запрещён")
    return p


def _check_shell_args(tokens: list[str]) -> None:
    """Блокирует передачу запрещённых имён или путей в аргументах команды."""
    for tok in tokens[1:]:
        if tok.startswith("-"):
            continue
        p = Path(tok)
        lower = tok.lower()
        if (
            p.name in DENY_NAMES
            or p.name.startswith(DENY_PREFIXES)
            or p.name.endswith(DENY_SUFFIXES)
            or DENY_PARTS.intersection(p.parts)
            or any(part in lower for part in ("secure_folder", ".git", ".env"))
        ):
            raise PermissionError(f"Запрещённый путь в аргументах команды: {tok}")


def _clip_stream(text: str, label: str) -> tuple[str, bool]:
    if len(text) <= MAX_STREAM_CHARS:
        return text, False
    return f"...(обрезано начало {label})...\n" + text[-MAX_STREAM_CHARS:], True


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
        return {
            "ok": True,
            "text": data.decode("utf-8", errors="replace"),
            "truncated": size > MAX_BYTES,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def write_file(path: str, content: str) -> dict:
    """Записать текст в файл (до 100 КБ)."""
    try:
        p = _safe(path)
        if len(content.encode("utf-8")) > MAX_BYTES:
            return {"ok": False, "error": f"Размер превышает лимит {MAX_BYTES} байт"}
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            f.write(content)
        return {"ok": True, "message": f"Файл {p.name} успешно записан"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def run_shell(cmd: str, cwd: str = ".", timeout: int = SHELL_TIMEOUT_SEC) -> dict:
    """Выполнить команду из белого списка в рамках ROOTS и вернуть вывод терминала."""
    try:
        work_dir = _safe(cwd)
        if not work_dir.is_dir():
            return {"ok": False, "error": "cwd не является каталогом"}

        tokens = shlex.split(cmd)
        if not tokens:
            return {"ok": False, "error": "Пустая команда"}

        bin_name = Path(tokens[0]).name
        if bin_name not in ALLOWED_BINS:
            return {"ok": False, "error": f"Команда '{bin_name}' не разрешена"}

        _check_shell_args(tokens)
        safe_timeout = max(1, min(int(timeout), 120))

        clean_env = {
            k: v
            for k, v in os.environ.items()
            if not any(s in k.upper() for s in ("KEY", "SECRET", "TOKEN", "PASS", "DSN"))
        }

        proc = subprocess.run(
            tokens,
            cwd=str(work_dir),
            env=clean_env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=safe_timeout,
            shell=False,
        )

        stdout, out_trunc = _clip_stream(proc.stdout, "stdout")
        stderr, err_trunc = _clip_stream(proc.stderr, "stderr")

        return {
            "ok": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "truncated": out_trunc or err_trunc,
        }
    except subprocess.TimeoutExpired as e:
        raw_out = e.stdout if isinstance(e.stdout, str) else (e.stdout or b"").decode("utf-8", errors="replace")
        raw_err = e.stderr if isinstance(e.stderr, str) else (e.stderr or b"").decode("utf-8", errors="replace")
        stdout, _ = _clip_stream(raw_out, "stdout")
        stderr, _ = _clip_stream(raw_err, "stderr")
        return {
            "ok": False,
            "returncode": -1,
            "error": f"Превышен таймаут {timeout}с",
            "stdout": stdout,
            "stderr": stderr,
            "truncated": True,
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


# Реестр: имя -> (функция, описание для модели)
TOOLS = {
    "list_dir": (list_dir, 'list_dir(path) - список содержимого каталога. Пример args: {"path": "."}'),
    "read_file": (read_file, 'read_file(path) - прочитать текстовый файл. Пример args: {"path": "agent_runner.py"}'),
    "write_file": (write_file, 'write_file(path, content) - записать текст в файл. Пример args: {"path": "test.txt", "content": "..."}'),
    "run_shell": (
        run_shell,
        'run_shell(cmd, cwd=".", timeout=30) - выполнить разрешённую shell-команду и прочитать stdout/stderr/returncode. '
        'Пример args: {"cmd": "python3 -m py_compile workspace_module/orchestrator.py", "cwd": "."}',
    ),
}