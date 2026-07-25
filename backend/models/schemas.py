"""
Shared Pydantic Contracts. Strictly typed. Frozen. Single-user boundary safe.
"""
from __future__ import annotations
from enum import Enum
from typing import Optional, Dict, List, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, PositiveInt, PositiveFloat

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ServiceResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    message: str
    trace_id: str
    duration_ms: PositiveFloat = 0.0

class RepoFileMeta(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    path: str
    size_bytes: PositiveInt
    language: str
    is_config: bool = False
    is_entrypoint: bool = False
    contains_secrets: bool = False

class RepoSummary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    total_files: PositiveInt
    languages: Dict[str, int]
    largest_files: List[str]
    entry_points: List[str]
    secrets_detected: PositiveInt = 0
    notes: str

class ScanResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    is_valid: bool
    summary: Optional[RepoSummary] = None
    warnings: List[str] = []
    scan_duration_ms: PositiveFloat = 0.0

class AIRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    prompt: str
    model: str
    context_limit: PositiveInt = 80000
    trace_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AIResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    content: str
    model_used: str
    tokens_used: Optional[PositiveInt] = None
    finish_reason: Optional[str] = None
    trace_id: str

class GitCommitPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    repo: str
    branch: str
    files: Dict[str, str]
    message: str

class GitCommitResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    committed_files: List[str]
    repo_url: Optional[str] = None
    branch: str
    commit_sha: Optional[str] = None
    trace_id: str

class ValidationResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    is_valid: bool
    file_count: PositiveInt = 0
    total_size_mb: PositiveFloat = 0.0
    rejected_files: List[str] = []
    error_message: Optional[str] = None

class SecurityReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    risk_level: RiskLevel = RiskLevel.LOW
    secrets_found: PositiveInt = 0
    dangerous_files: List[str] = []
    traversal_attempts: PositiveInt = 0
    recommendations: List[str] = []
