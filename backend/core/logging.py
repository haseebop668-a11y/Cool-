"""
Structured JSON Logger with Trace Context. Single-user optimized. Framework-agnostic.
"""
from __future__ import annotations
import logging
import json
import time
import uuid
from typing import Any, Dict, Optional
from contextvars import ContextVar

trace_ctx: ContextVar[str] = ContextVar("trace_id", default="")

class StructuredLogger:
    def __init__(self, name: str = "workbench-backend"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter("%(message)s"))
            self.logger.addHandler(h)

    def _build(self, level: str, msg: str, extra: Dict[str, Any]) -> str:
        return json.dumps({
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "lvl": level,
            "trace": trace_ctx.get() or str(uuid.uuid4())[:8],
            "msg": msg,
            **extra
        })

    def info(self, msg: str, **kw): self.logger.info(self._build("INFO", msg, kw))
    def warn(self, msg: str, **kw): self.logger.warning(self._build("WARN", msg, kw))
    def error(self, msg: str, **kw): self.logger.error(self._build("ERROR", msg, kw))

logger = StructuredLogger()
