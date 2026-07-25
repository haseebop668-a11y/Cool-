"""Secure local session adapter. Bridges UI state proxy with backend security contracts."""
from __future__ import annotations
from typing import Any, Dict, Optional
from core.security import encrypt_token, decrypt_token
from core.exceptions import SecurityError
from core.logging import logger

class SessionService:
    def __init__(self, encryption_key: str) -> None:
        self._key = encryption_key

    def lock_credentials(self, state: Dict[str, Any], or_key: str, git_pat: str) -> None:
        state["or_token_enc"] = encrypt_token(or_key, self._key)
        state["git_token_enc"] = encrypt_token(git_pat, self._key)
        state["creds_locked"] = True
        logger.info("Credentials locked in local session")

    def unlock_credentials(self, state: Dict[str, Any]) -> None:
        state.pop("or_token_enc", None)
        state.pop("git_token_enc", None)
        state["creds_locked"] = False
        logger.info("Credentials unlocked from local session")

    def get_or_key(self, state: Dict[str, Any]) -> str:
        enc = state.get("or_token_enc")
        if not enc: raise SecurityError("OpenRouter key not locked in session")
        return decrypt_token(enc, self._key)

    def get_git_pat(self, state: Dict[str, Any]) -> str:
        enc = state.get("git_token_enc")
        if not enc: raise SecurityError("GitHub PAT not locked in session")
        return decrypt_token(enc, self._key)

    def set_repo_summary(self, state: Dict[str, Any], summary: dict) -> None:
        state["repo_summary"] = summary

    def get_repo_summary(self, state: Dict[str, Any]) -> Optional[dict]:
        return state.get("repo_summary")
