"""
Lightweight Dependency Injection Container.
Explicit registration. Singleton lifecycle. No reflection. Single-user optimized.
"""
from __future__ import annotations
import threading
from typing import TypeVar, Type, Callable, Any, Dict, Literal
from core.config import Settings

T = TypeVar("T")

class DIContainer:
    def __init__(self) -> None:
        self._factories: Dict[Type[Any], Callable[..., Any]] = {}
        self._scopes: Dict[Type[Any], str] = {}
        self._singletons: Dict[Type[Any], Any] = {}
        self._overrides: Dict[Type[Any], Any] = {}
        self._lock = threading.Lock()

    def register(self, interface: Type[T], factory: Callable[..., T], scope: Literal["singleton", "transient"] = "singleton") -> None:
        self._factories[interface] = factory
        self._scopes[interface] = scope
        self._singletons.pop(interface, None)

    def resolve(self, interface: Type[T]) -> T:
        if interface in self._overrides:
            return self._overrides[interface]
        if interface not in self._factories:
            raise KeyError(f"Service {interface.__name__} not registered.")
        if self._scopes[interface] == "singleton":
            with self._lock:
                if interface not in self._singletons:
                    self._singletons[interface] = self._factories[interface]()
                return self._singletons[interface]
        return self._factories[interface]()

    def override(self, interface: Type[T], instance: T) -> None:
        self._overrides[interface] = instance

    def reset(self) -> None:
        self._overrides.clear()
        self._singletons.clear()

def build_container(settings: Settings) -> DIContainer:
    container = DIContainer()
    from services.openrouter import OpenRouterClient
    from services.github import GitHubClient
    from services.session_store import SessionService
    from services.compression import CompressionService
    from services.repo_scanner import RepoScannerService

    container.register(OpenRouterClient, lambda: OpenRouterClient(
        api_key=settings.openrouter.api_key.get_secret_value(),
        base_url=str(settings.openrouter.base_url),
        model=settings.openrouter.model,
        timeout_sec=settings.openrouter.timeout_sec,
        max_retries=settings.openrouter.max_retries,
        retry_base_delay=settings.openrouter.retry_base_delay
    ), scope="singleton")

    container.register(GitHubClient, lambda: GitHubClient(
        pat=settings.github.pat.get_secret_value(),
        base_url=str(settings.github.api_base_url),
        timeout_sec=settings.github.timeout_sec,
        max_retries=settings.github.max_retries,
        default_branch=settings.github.default_branch
    ), scope="singleton")

    container.register(SessionService, lambda: SessionService(
        encryption_key=settings.security.session_encryption_key.get_secret_value()
    ), scope="singleton")

    container.register(CompressionService, lambda: CompressionService(
        max_size_mb=settings.security.max_zip_size_mb,
        max_files=settings.security.max_zip_files,
        allow_executables=settings.security.allow_executables
    ), scope="singleton")

    container.register(RepoScannerService, lambda: RepoScannerService(
        max_context_chars=settings.performance.max_context_chars
    ), scope="singleton")

    return container
