"""Аудит .py файлов в каталоге на соблюдение лимита 200 строк."""

from pathlib import Path
from typing import Any, Dict, List

SKIP_DIRS = {"__pycache__", ".venv", "venv", ".git", ".cto_agent"}
MAX_LINES_LIMIT = 200


class AuditTool:
    """Проверяет количество строк в Python-файлах рабочего пространства."""

    def __init__(
        self,
        target_dir: str | Path = "workspace_module",
        line_limit: int = MAX_LINES_LIMIT,
    ) -> None:
        self.target_dir = Path(target_dir).resolve()
        self.line_limit = line_limit

    def check_line_counts(self) -> Dict[str, int]:
        results: Dict[str, int] = {}
        if not self.target_dir.exists() or not self.target_dir.is_dir():
            return results

        for path in sorted(self.target_dir.rglob("*.py")):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.is_file():
                with path.open("r", encoding="utf-8") as f:
                    results[str(path)] = sum(1 for _ in f)
        return results

    def run_report(self) -> Dict[str, int]:
        """Возвращает словарь {путь: кол-во_строк} для файлов сверх лимита."""
        counts = self.check_line_counts()
        return {p: c for p, c in counts.items() if c > self.line_limit}

    def summary(self) -> Dict[str, Any]:
        counts = self.check_line_counts()
        violations = {p: c for p, c in counts.items() if c > self.line_limit}
        max_lines = max(counts.values(), default=0)
        offenders: List[str] = list(violations.keys())
        return {
            "ok": len(violations) == 0,
            "checked_files": len(counts),
            "line_limit": self.line_limit,
            "max_lines": max_lines,
            "violations": violations,
            "offenders": offenders,
        }