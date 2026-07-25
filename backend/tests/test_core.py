"""Unit tests for core infrastructure modules."""
import pytest
from pydantic import ValidationError
from core.config import Settings, SecuritySettings
from core.security import encrypt_token, decrypt_token, validate_path
from core.dependencies import DIContainer

def test_config_validation():
    with pytest.raises(ValidationError):
        SecuritySettings(session_encryption_key="invalid")

def test_token_encryption_roundtrip():
    key = "dGhpcyBpcyBhIHRlc3Qga2V5IGZvciBmZXJuZXQh"
    raw = "sk-test-1234567890abcdef"
    enc = encrypt_token(raw, key)
    assert enc != raw
    assert decrypt_token(enc, key) == raw

def test_path_sanitization():
    assert validate_path("src/main.py") == "src/main.py"
    with pytest.raises(Exception):
        validate_path("../../../etc/passwd")

def test_di_container_resolution():
    container = DIContainer()
    container.register(str, lambda: "resolved", scope="singleton")
    assert container.resolve(str) == "resolved"

def test_di_container_override():
    container = DIContainer()
    container.register(int, lambda: 1)
    container.override(int, 99)
    assert container.resolve(int) == 99
    container.reset()
    assert container.resolve(int) == 1
