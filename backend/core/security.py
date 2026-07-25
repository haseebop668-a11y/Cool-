"""
Local Session Security & Path Validation. Fernet encryption. Zero secret leakage.
"""
from __future__ import annotations
import re
import base64
from cryptography.fernet import Fernet
from core.exceptions import SecurityError, ValidationError

def encrypt_token(token: str, key: str) -> str:
    cipher = Fernet(key.encode())
    return base64.b64encode(cipher.encrypt(token.encode())).decode()

def decrypt_token(enc: str, key: str) -> str:
    try:
        cipher = Fernet(key.encode())
        return cipher.decrypt(base64.b64decode(enc)).decode()
    except Exception as e:
        raise SecurityError("Token decryption failed. Session corrupted.") from e

def validate_path(p: str) -> str:
    clean = re.sub(r"[^\w\-.\/]", "_", p)
    if ".." in clean or clean.startswith("/"):
        raise ValidationError(f"Path traversal blocked: {p}")
    return clean
