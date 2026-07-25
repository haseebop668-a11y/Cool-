"""Unit tests for service layer business logic."""
import pytest
import zipfile
import io
from services.compression import CompressionService
from services.repo_scanner import RepoScannerService

@pytest.fixture
def zip_bytes():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("main.py", "print('hello')")
        z.writestr("config.json", '{"key": "val"}')
    return buf.getvalue()

def test_compression_validation(zip_bytes):
    svc = CompressionService(max_size_mb=10, max_files=100, allow_executables=False)
    res = svc.validate(zip_bytes)
    assert res.success is True

def test_compression_streaming(zip_bytes):
    svc = CompressionService(max_size_mb=10, max_files=100, allow_executables=False)
    files = list(svc.stream(zip_bytes))
    assert len(files) == 2
    assert files[0][0] == "main.py"

def test_repo_scanner(zip_bytes):
    svc = CompressionService(max_size_mb=10, max_files=100, allow_executables=False)
    files = list(svc.stream(zip_bytes))
    scanner = RepoScannerService(max_context_chars=50000)
    summary = scanner.scan(files)
    assert summary.total_files == 2
    assert "Python" in summary.languages
    assert summary.secrets_detected == 0
