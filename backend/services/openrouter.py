"""OpenRouter AI inference client with retry, rate-limit handling, and structured logging."""
from __future__ import annotations
import requests
import time
import uuid
from typing import Optional
from models.schemas import ServiceResult
from core.exceptions import APIError, RateLimitError
from core.logging import logger
from utils.retry import retry_api

class OpenRouterClient:
    def __init__(self, api_key: str, base_url: str, model: str, timeout_sec: int, max_retries: int, retry_base_delay: float) -> None:
        self.key = api_key
        self.url = base_url
        self.model = model
        self.timeout = timeout_sec
        self.max_retries = max_retries
        self.retry_base_delay = retry_base_delay

    @retry_api(max_attempts=3, base_delay=1.5)
    def generate(self, prompt: str, trace_id: Optional[str] = None) -> ServiceResult:
        tid = trace_id or str(uuid.uuid4())[:8]
        start = time.perf_counter()
        logger.info("OpenRouter request started", trace=tid, model=self.model, prompt_len=len(prompt))
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json", "HTTP-Referer": "https://ai-workbench.local"}
        payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
        try:
            res = requests.post(self.url, headers=headers, json=payload, timeout=self.timeout)
            dur = (time.perf_counter() - start) * 1000
            if res.status_code == 200:
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                logger.info("OpenRouter success", trace=tid, duration_ms=round(dur, 2))
                return ServiceResult(success=True, data={"content": content}, message="OK", trace_id=tid, duration_ms=dur)
            elif res.status_code == 429:
                raise RateLimitError("OpenRouter rate limit", retry_after=5.0, trace_id=tid)
            elif res.status_code >= 500:
                raise APIError(f"Server error {res.status_code}", res.status_code, trace_id=tid)
            else:
                raise APIError(f"Client error {res.status_code}: {res.text}", res.status_code, trace_id=tid)
        except requests.Timeout:
            raise APIError("Gateway timeout", 504, trace_id=tid)
        except Exception as e:
            raise APIError(f"Network failure: {e}", 0, trace_id=tid)
