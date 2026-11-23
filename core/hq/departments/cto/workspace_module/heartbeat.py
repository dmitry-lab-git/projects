"""Модуль фиксации пульса (heartbeat) рабочего пространства."""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class _FallbackHeartbeatLogger:
    """Резервный логгер пульса, если внешний трекер не передан."""

    def log_status(self, stage: str, state: str, detail: str = "") -> None:
        msg = f"[{stage}] {state}" + (f": {detail}" if detail else "")
        logger.info(msg)


class Heartbeat:
    """Фиксирует сигналы активности без блокировки основного цикла."""

    def __init__(self, status_logger: Optional[Any] = None) -> None:
        self.tracker = (
            status_logger if status_logger is not None else _FallbackHeartbeatLogger()
        )

    def emit(self, detail: str = "") -> None:
        """Отправляет разовый сигнал активности."""
        self.tracker.log_status("HEARTBEAT", "alive", detail)