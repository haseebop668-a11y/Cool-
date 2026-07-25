"""GitHub REST API client for secure, conflict-aware file deployment."""
from __future__ import annotations
import requests
import base64
import time
import uuid
from typing import Optional
from models.schemas import ServiceResult, GitCommitPayload
from core.exceptions import APIError
from core.logging import logger
from utils.retry import retry_api

class GitHubClient:
    def __init__(self, pat: str, base_url: str, timeout_sec: int, max_retries: int, default_branch: str) -> None:
        self.pat = pat
        self.timeout = timeout_sec
        self.default_branch = default_branch
        self.headers = {"Authorization": f"token {pat}", "Accept": "application/vnd.github.v3+json"}
        self.base_url = base_url.rstrip("/")

    @retry_api(max_attempts=2, base_delay=1.0)
    def push_files(self, payload: GitCommitPayload, trace_id: Optional[str] = None) -> ServiceResult:
        tid = trace_id or str(uuid.uuid4())[:8]
        start = time.perf_counter()
        branch = payload.branch or self.default_branch
        logger.info("GitHub push started", trace=tid, repo=payload.repo, files=len(payload.files), branch=branch)
        api_base = f"{self.base_url}/repos/{payload.repo}/contents"
        committed = []
        try:
            for path, content in payload.files.items():
                url = f"{api_base}/{path}"
                sha = None
                try:
                    r = requests.get(url, headers=self.headers, params={"ref": branch}, timeout=10)
                    if r.status_code == 200: sha = r.json().get("sha")
                except: pass
                enc = base64.b64encode(content.encode()).decode()
                body = {"message": payload.message, "content": enc, "branch": branch}
                if sha: body["sha"] = sha
                put = requests.put(url, headers=self.headers, json=body, timeout=self.timeout)
                if put.status_code == 409:
                    raise APIError("Git conflict (409): Stale SHA. Retry required.", 409, trace_id=tid)
                if put.status_code not in (200, 201):
                    err = put.json().get("message", put.text) if put.headers.get("content-type","").startswith("application/json") else put.text
                    raise APIError(f"GitHub error {put.status_code}: {err}", put.status_code, trace_id=tid)
                committed.append(path)
            dur = (time.perf_counter() - start) * 1000
            logger.info("GitHub push success", trace=tid, duration_ms=round(dur, 2))
            return ServiceResult(success=True, data={"committed": committed}, message="Push complete", trace_id=tid, duration_ms=dur)
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Push failed: {e}", 0, trace_id=tid)
