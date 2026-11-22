"""Хранение контекста диалога, журнала событий и кеша ответов модели."""
import hashlib
import json
import time
from pathlib import Path
from typing import Callable, Optional


def _files_fingerprint(roots: list[Path]) -> str:
    """Снимок mtime и размеров файлов в разрешённых корнях для инвалидации кеша."""
    h = hashlib.sha256()
    for root in roots:
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if any(part in {".git", "__pycache__", "venv", ".cto_agent"} for part in p.parts):
                continue
            if p.is_file():
                try:
                    st = p.stat()
                    h.update(f"{p}:{st.st_mtime_ns}:{st.st_size}\n".encode("utf-8"))
                except OSError:
                    continue
    return h.hexdigest()


class ResponseCache:
    """Файловый кеш ответов модели с TTL и инвалидацией при изменении файлов проекта."""

    def __init__(
        self,
        cache_path: Path,
        roots: Optional[list[Path]] = None,
        ttl_sec: int = 3600,
        enabled: bool = True,
    ) -> None:
        self.cache_path = cache_path
        self.roots = list(roots or [])
        self.ttl_sec = ttl_sec
        self.enabled = enabled
        self.hits = 0
        self.misses = 0
        self._data: dict[str, dict] = self._load()

    def _load(self) -> dict[str, dict]:
        if not self.cache_path.is_file():
            return {}
        try:
            raw = json.loads(self.cache_path.read_text(encoding="utf-8"))
            return raw if isinstance(raw, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _flush(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.cache_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.cache_path)

    def _make_key(self, prompt: str, target_name: str) -> str:
        fp = _files_fingerprint(self.roots) if self.roots else ""
        payload = f"{target_name}\n{fp}\n{prompt}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def get(self, prompt: str, target_name: str = "technical") -> Optional[str]:
        if not self.enabled:
            return None
        key = self._make_key(prompt, target_name)
        entry = self._data.get(key)
        if not entry:
            self.misses += 1
            return None
        if time.time() - float(entry.get("created_at", 0)) > self.ttl_sec:
            self._data.pop(key, None)
            self._flush()
            self.misses += 1
            return None
        self.hits += 1
        return entry.get("reply")

    def put(self, prompt: str, reply: str, target_name: str = "technical") -> None:
        if not self.enabled or not reply:
            return
        key = self._make_key(prompt, target_name)
        self._data[key] = {
            "created_at": time.time(),
            "target_name": target_name,
            "reply": reply,
        }
        self._flush()

    def clear(self) -> int:
        count = len(self._data)
        self._data.clear()
        self.hits = 0
        self.misses = 0
        if self.cache_path.exists():
            self.cache_path.unlink()
        return count

    def wrap_caller(
        self,
        call_model: Callable[[str], Optional[str]],
        target_name: str = "technical",
        on_hit: Optional[Callable[[], None]] = None,
    ) -> Callable[[str], Optional[str]]:
        """Оборачивает call_model: при попадании в кеш не тратит RPM и не ходит в API."""
        def wrapped(prompt: str) -> Optional[str]:
            cached = self.get(prompt, target_name=target_name)
            if cached is not None:
                if on_hit:
                    on_hit()
                return cached
            reply = call_model(prompt)
            if reply is not None:
                self.put(prompt, reply, target_name=target_name)
            return reply

        return wrapped


class ContextStore:
    """Автоматическое сохранение и восстановление истории диалога (history)."""

    def __init__(self, context_path: Path) -> None:
        self.context_path = context_path

    def load(self) -> list:
        if not self.context_path.is_file():
            return []
        try:
            data = json.loads(self.context_path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []

    def save(self, history: list) -> None:
        self.context_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.context_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.context_path)

    def clear(self) -> None:
        self.save([])


class SessionLogger:
    """Append-only журнал всех событий диалога и шагов агента (JSONL)."""

    def __init__(self, log_path: Path, source_uuid: str) -> None:
        self.log_path = log_path
        self.source_uuid = source_uuid

    def log(self, event_type: str, **payload) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "source_uuid": self.source_uuid,
            "type": event_type,
            **payload,
        }
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")