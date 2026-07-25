"""
Core Exception Hierarchy. Strictly typed. Framework-agnostic. Single-user boundary safe.
"""
from __future__ import annotations
import re
from enum import Enum
from typing import Optional

_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")

class ErrorCode(str, Enum):
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    SECURITY_ERROR = "SECURITY_ERROR"
    API_ERROR = "API_ERROR"
    RATE_LIMIT = "RATE_LIMIT"

class AppError(Exception):
    def __init__(self, message: str, code: str = ErrorCode.INTERNAL_ERROR.value, trace_id: Optional[str] = None) -> None:
        if not isinstance(message, str) or not message.strip():
            raise ValueError("AppError message must be a non-empty string.")
        if not _CODE_PATTERN.match(code):
            raise ValueError(f"Invalid error code format: {code!r}")
        super().__init__(message)
        self.message = message
        self.code = code
        self.trace_id = trace_id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code={self.code!r}, message={self.message!r}, trace_id={self.trace_id!r})"

    def __str__(self) -> str:
        trace = f" [trace:{self.trace_id}]" if self.trace_id else ""
        return f"[{self.code}] {self.message}{trace}"

class ValidationError(AppError):
    def __init__(self, message: str, trace_id: Optional[str] = None) -> None:
        super().__init__(message=message, code=ErrorCode.VALIDATION_ERROR.value, trace_id=trace_id)

class SecurityError(AppError):
    def __init__(self, message: str, trace_id: Optional[str] = None) -> None:
        super().__init__(message=message, code=ErrorCode.SECURITY_ERROR.value, trace_id=trace_id)

class APIError(AppError):
    def __init__(self, message: str, status_code: int, code: str = ErrorCode.API_ERROR.value, trace_id: Optional[str] = None) -> None:
        if not isinstance(status_code, int) or not (100 <= status_code <= 599):
            raise ValueError(f"Invalid HTTP status code: {status_code}")
        super().__init__(message=message, code=code, trace_id=trace_id)
        self.status_code = status_code

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(status_code={self.status_code}, code={self.code!r}, message={self.message!r}, trace_id={self.trace_id!r})"

class RateLimitError(APIError):
    def __init__(self, message: str, retry_after: float = 5.0, trace_id: Optional[str] = None) -> None:
        if not isinstance(retry_after, (int, float)) or retry_after < 0.0:
            raise ValueError(f"Invalid retry_after: {retry_after}")
        super().__init__(message=message, status_code=429, code=ErrorCode.RATE_LIMIT.value, trace_id=trace_id)
        self.retry_after = float(retry_after)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(retry_after={self.retry_after}, code={self.code!r}, message={self.message!r}, trace_id={self.trace_id!r})"

__all__ = ["ErrorCode", "AppError", "ValidationError", "SecurityError", "APIError", "RateLimitError"]
