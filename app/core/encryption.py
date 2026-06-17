"""Encryption utilities for sensitive data like API keys"""
from cryptography.fernet import Fernet
from app.core.config import settings
import base64
import hashlib


def get_encryption_key() -> bytes:
    """Derive encryption key from SECRET_KEY"""
    # Use SECRET_KEY from settings to derive a Fernet key
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key"""
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key"""
    f = Fernet(get_encryption_key())
    decrypted = f.decrypt(encrypted_key.encode())
    return decrypted.decode()


def get_key_preview(api_key: str) -> str:
    """Get a masked preview of an API key (last 4 chars)"""
    if len(api_key) <= 4:
        return "***"
    return f"...{api_key[-4:]}"
