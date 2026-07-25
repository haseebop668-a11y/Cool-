"""
Application Bootstrap & Backend Facade.
Composition root. DI wiring. Exception boundary. Single-user optimized.
"""
from __future__ import annotations
import time
import uuid
from typing import Dict, Any, Optional
from core.config import Settings
from core.dependencies import DIContainer
from core.logging import logger, trace_ctx
from core.exceptions import AppError, SecurityError, APIError, RateLimitError, ValidationError
from models.schemas import ServiceResult, GitCommitPayload
from services.compression import CompressionService
from services.repo_scanner import RepoScannerService
from services.openrouter import OpenRouterClient
from services.github import GitHubClient
from services.session_store import SessionService

class BackendFacade:
    def __init__(self, container: DIContainer) -> None:
        self._container = container
        self._session: SessionService = container.resolve(SessionService)
        self._compression: CompressionService = container.resolve(CompressionService)
        self._scanner: RepoScannerService = container.resolve(RepoScannerService)
        self._ai: OpenRouterClient = container.resolve(OpenRouterClient)
        self._git: GitHubClient = container.resolve(GitHubClient)
        logger.info("BackendFacade initialized via DI container")

    def _trace(self) -> str:
        tid = str(uuid.uuid4())[:8]
        trace_ctx.set(tid)
        return tid

    def _map_result(self, success: bool, message: str, trace_id: str, duration_ms: float, data: Optional[Dict[str, Any]] = None, error_code: Optional[str] = None) -> ServiceResult:
        return ServiceResult(success=success, data=data, error_code=error_code, message=message, trace_id=trace_id, duration_ms=round(duration_ms, 2))

    def lock_credentials(self, state: Dict[str, Any], or_key: str, git_pat: str) -> ServiceResult:
        tid = self._trace()
        start = time.perf_counter()
        try:
            self._session.lock_credentials(state, or_key, git_pat)
            return self._map_result(True, "Credentials secured", tid, (time.perf_counter() - start) * 1000)
        except Exception as e:
            logger.error("Credential lock failed", trace=tid, error=str(e))
            return self._map_result(False, str(e), tid, (time.perf_counter() - start) * 1000, error_code="SECURITY_ERROR")

    def unlock_credentials(self, state: Dict[str, Any]) -> ServiceResult:
        tid = self._trace()
        start = time.perf_counter()
        try:
            self._session.unlock_credentials(state)
            return self._map_result(True, "Credentials cleared", tid, (time.perf_counter() - start) * 1000)
        except Exception as e:
            return self._map_result(False, str(e), tid, (time.perf_counter() - start) * 1000, error_code="SECURITY_ERROR")

    def validate_and_scan_repo(self, state: Dict[str, Any], zip_data: bytes) -> ServiceResult:
        tid = self._trace()
        start = time.perf_counter()
        try:
            val_res = self._compression.validate(zip_data)
            if not val_res.success:
                return self._map_result(False, val_res.message, tid, (time.perf_counter() - start) * 1000, error_code="VALIDATION_ERROR")
            files = list(self._compression.stream(zip_data))
            summary = self._scanner.scan(files)
            self._session.set_repo_summary(state, summary.model_dump())
            return self._map_result(True, "Repository scanned", tid, (time.perf_counter() - start) * 1000, data=summary.model_dump())
        except ValidationError as e:
            return self._map_result(False, str(e), tid, (time.perf_counter() - start) * 1000, error_code="VALIDATION_ERROR")
        except Exception as e:
            logger.error("Repo scan pipeline failed", trace=tid, error=str(e))
            return self._map_result(False, str(e), tid, (time.perf_counter() - start) * 1000, error_code="PIPELINE_ERROR")

    def generate_ai_response(self, state: Dict[str, Any], prompt: str) -> ServiceResult:
        tid = self._trace()
        start = time.perf_counter()
        try:
            or_key = self._session.get_or_key(state)
            self._ai.key = or_key
            summary = self._session.get_repo_summary(state)
            context = f"Repository Context: {summary.get('notes', '')}\nLanguages: {summary.get('languages', {})}\n\n" if summary else ""
            res = self._ai.generate(f"{context}User Directive:\n{prompt}", trace_id=tid)
            duration = (time.perf_counter() - start) * 1000
            if res.success:
                return self._map_result(True, "OK", tid, duration, data=res.data)
            return self._map_result(False, res.message, tid, duration, error_code=res.error_code or "AI_ERROR")
        except SecurityError as e:
            return self._map_result(False, str(e), tid, (time.perf_counter() - start) * 1000, error_code="AUTH_MISSING")
        except RateLimitError as e:
            return self._map_result(False, str(e), tid, (time.perf_counter() - start) * 1000, error_code="RATE_LIMIT")
        except Exception as e:
            logger.error("AI pipeline failed", trace=tid, error=str(e))
            return self._map_result(False, str(e), tid, (time.perf_counter() - start) * 1000, error_code="AI_ERROR")

    def deploy_to_github(self, state: Dict[str, Any], repo: str, branch: str, files: Dict[str, str], message: str) -> ServiceResult:
        tid = self._trace()
        start = time.perf_counter()
        try:
            pat = self._session.get_git_pat(state)
            self._git.pat = pat
            self._git.headers["Authorization"] = f"token {pat}"
            payload = GitCommitPayload(repo=repo, branch=branch, files=files, message=message)
            res = self._git.push_files(payload, trace_id=tid)
            duration = (time.perf_counter() - start) * 1000
            if res.success:
                return self._map_result(True, "Push complete", tid, duration, data=res.data)
            return self._map_result(False, res.message, tid, duration, error_code=res.error_code or "DEPLOY_ERROR")
        except SecurityError as e:
            return self._map_result(False, str(e), tid, (time.perf_counter() - start) * 1000, error_code="AUTH_MISSING")
        except APIError as e:
            return self._map_result(False, str(e), tid, (time.perf_counter() - start) * 1000, error_code="API_ERROR")
        except Exception as e:
            logger.error("Deployment pipeline failed", trace=tid, error=str(e))
            return self._map_result(False, str(e), tid, (time.perf_counter() - start) * 1000, error_code="DEPLOY_ERROR")

def initialize_backend(env_file: Optional[str] = None) -> BackendFacade:
    logger.info("Initializing backend infrastructure")
    settings = Settings.load(env_file)
    container = DIContainer()
    container.register(SessionService, lambda: SessionService(encryption_key=settings.security.session_encryption_key.get_secret_value()), scope="singleton")
    container.register(CompressionService, lambda: CompressionService(max_size_mb=settings.security.max_zip_size_mb, max_files=settings.security.max_zip_files, allow_executables=settings.security.allow_executables), scope="singleton")
    container.register(RepoScannerService, lambda: RepoScannerService(max_context_chars=settings.performance.max_context_chars), scope="singleton")
    container.register(OpenRouterClient, lambda: OpenRouterClient(api_key=settings.openrouter.api_key.get_secret_value(), base_url=str(settings.openrouter.base_url), model=settings.openrouter.model, timeout_sec=settings.openrouter.timeout_sec, max_retries=settings.openrouter.max_retries, retry_base_delay=settings.openrouter.retry_base_delay), scope="singleton")
    container.register(GitHubClient, lambda: GitHubClient(pat=settings.github.pat.get_secret_value(), base_url=str(settings.github.api_base_url), timeout_sec=settings.github.timeout_sec, max_retries=settings.github.max_retries, default_branch=settings.github.default_branch), scope="singleton")
    logger.info("DI container built and services registered")
    return BackendFacade(container)
