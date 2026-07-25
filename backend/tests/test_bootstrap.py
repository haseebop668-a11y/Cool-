"""Integration test for backend bootstrap and facade wiring."""
import pytest
import os
from bootstrap import initialize_backend

def test_facade_initialization():
    os.environ["SECURITY__SESSION_ENCRYPTION_KEY"] = "dGhpcyBpcyBhIHRlc3Qga2V5IGZvciBmZXJuZXQh"
    os.environ["OPENROUTER__API_KEY"] = "sk-dummy"
    os.environ["GITHUB__PAT"] = "ghp_dummy"
    facade = initialize_backend()
    assert facade is not None
    assert facade.settings.app.env.value == "local"
    assert facade.ai_client is not None
    assert facade.git_client is not None
