"""
Personal Workbench Configuration Layer.
Single-user focused. Loads from .env. Pydantic v2 validated. Immutable.
"""
from __future__ import annotations
from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic import SecretStr, Field, field_validator, HttpUrl, PositiveInt, PositiveFloat
from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet

class Environment(str, Enum):
    LOCAL = "local"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, extra="ignore")
    env: Environment = Field(default=Environment.LOCAL)
    app_name: str = Field(default="ai-workbench")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)

class SecuritySettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, extra="ignore")
    session_encryption_key: SecretStr = Field(description="Fernet key for local session encryption")
    max_zip_size_mb: PositiveInt = Field(default=150)
    max_zip_files: PositiveInt = Field(default=5000)
    allow_executables: bool = Field(default=False)

    @field_validator("session_encryption_key", mode="before")
    @classmethod
    def _validate_fernet_key(cls, v: str | SecretStr) -> SecretStr:
        raw = v.get_secret_value() if isinstance(v, SecretStr) else v
        try:
            Fernet(raw.encode() if isinstance(raw, str) else raw)
        except Exception as e:
            raise ValueError(f"Invalid Fernet key: {e}") from e
        return SecretStr(raw)

class OpenRouterSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, extra="ignore")
    api_key: SecretStr = Field(description="OpenRouter token")
    base_url: HttpUrl = Field(default="https://openrouter.ai/api/v1/chat/completions")
    model: str = Field(default="qwen/qwen-2.5-coder-7b-instruct:free")
    timeout_sec: PositiveInt = Field(default=90)
    max_retries: PositiveInt = Field(default=3)
    retry_base_delay: PositiveFloat = Field(default=1.0)

class GitHubSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, extra="ignore")
    pat: SecretStr = Field(description="GitHub Personal Access Token")
    api_base_url: HttpUrl = Field(default="https://api.github.com")
    timeout_sec: PositiveInt = Field(default=20)
    max_retries: PositiveInt = Field(default=2)
    default_branch: str = Field(default="main")

class LoggingSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, extra="ignore")
    level: LogLevel = Field(default=LogLevel.INFO)
    json_format: bool = Field(default=True)
    include_trace: bool = Field(default=True)

class PerformanceSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, extra="ignore")
    max_context_chars: PositiveInt = Field(default=80000)
    stream_chunk_size_kb: PositiveInt = Field(default=512)
    enable_caching: bool = Field(default=True)
    cache_ttl_sec: PositiveInt = Field(default=300)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", case_sensitive=False, extra="ignore", frozen=True
    )
    app: AppSettings = Field(default_factory=AppSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    openrouter: OpenRouterSettings = Field(default_factory=OpenRouterSettings)
    github: GitHubSettings = Field(default_factory=GitHubSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)

    @classmethod
    def load(cls, env_file: Optional[str | Path] = None) -> Settings:
        return cls(_env_file=env_file) if env_file else cls()
