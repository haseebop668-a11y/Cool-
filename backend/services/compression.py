"""Archive compression, validation, and streaming extraction service."""
from __future__ import annotations
import zipfile
import io
import time
import uuid
from typing import Iterator, Tuple
from pathlib import Path
from core.security import validate_path
from core.logging import logger
from core.exceptions import ValidationError
from models.schemas import ServiceResult

class CompressionService:
    def __init__(self, max_size_mb: int, max_files: int, allow_executables: bool) -> None:
        self.max_size_mb = max_size_mb
        self.max_files = max_files
        self.allow_executables = allow_executables
        self._dangerous_ext = {".exe",".bin",".dll",".so",".dylib",".msi",".bat",".cmd",".ps1",".sh",".scr"}

    def validate(self, data: bytes) -> ServiceResult:
        tid = str(uuid.uuid4())[:8]
        start = time.perf_counter()
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                if len(z.infolist()) > self.max_files:
                    raise ValidationError(f"Archive exceeds {self.max_files} files")
                total = sum(i.file_size for i in z.infolist())
                if total > self.max_size_mb * 1024 * 1024:
                    raise ValidationError(f"Archive exceeds {self.max_size_mb}MB uncompressed")
                for i in z.infolist():
                    if i.is_dir(): continue
                    ext = Path(i.filename).suffix.lower()
                    if not self.allow_executables and ext in self._dangerous_ext:
                        raise ValidationError(f"Executable blocked: {i.filename}")
                    if ".." in i.filename or i.filename.startswith("/"):
                        raise ValidationError(f"Path traversal blocked: {i.filename}")
            dur = (time.perf_counter() - start) * 1000
            logger.info("ZIP validation passed", trace=tid, duration_ms=round(dur, 2))
            return ServiceResult(success=True, message="Archive validated", trace_id=tid, duration_ms=dur)
        except Exception as e:
            dur = (time.perf_counter() - start) * 1000
            logger.error("ZIP validation failed", trace=tid, error=str(e), duration_ms=round(dur, 2))
            return ServiceResult(success=False, error_code="VALIDATION_ERROR", message=str(e), trace_id=tid, duration_ms=dur)

    def stream(self, data: bytes) -> Iterator[Tuple[str, str]]:
        tid = str(uuid.uuid4())[:8]
        logger.info("Streaming ZIP archive", trace=tid, size_mb=round(len(data)/1024/1024, 2))
        with zipfile.ZipFile(io.BytesIO(data), "r") as z:
            for info in z.infolist():
                if info.is_dir(): continue
                safe = validate_path(info.filename)
                try:
                    with z.open(info.filename) as f:
                        yield safe, f.read().decode("utf-8", errors="ignore")
                except Exception as e:
                    logger.warn(f"Skipped file during stream", trace=tid, file=info.filename, reason=str(e))
