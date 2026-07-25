"""Exponential backoff retry decorator for external API clients."""
from __future__ import annotations
import time
import random
import functools
from typing import Callable, TypeVar, Any
from core.exceptions import APIError, RateLimitError
from core.logging import logger

T = TypeVar("T")

def retry_api(max_attempts: int = 3, base_delay: float = 1.0) -> Callable:
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except RateLimitError as e:
                    last_exc = e
                    delay = e.retry_after + random.uniform(0, 0.5)
                    logger.warn(f"Rate limit hit. Retry {attempt}/{max_attempts} in {delay:.1f}s")
                    time.sleep(delay)
                except APIError as e:
                    last_exc = e
                    if e.status_code < 500:
                        raise
                    delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                    logger.warn(f"API error {e.status_code}. Retry {attempt}/{max_attempts} in {delay:.1f}s")
                    time.sleep(delay)
                except Exception as e:
                    last_exc = e
                    break
            raise last_exc # type: ignore
        return wrapper
    return decorator
