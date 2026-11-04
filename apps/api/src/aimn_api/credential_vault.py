"""Authenticated encryption helpers for provider credential payloads.

Only encrypted envelopes should be persisted. The encryption key belongs in the
deployment secret store and must never be stored beside the ciphertext.
"""
from __future__ import annotations

import json
import os
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

_PREFIX = "aimn:v1:"
_ENV_KEY = "AIMN_CREDENTIAL_ENCRYPTION_KEY"


class CredentialVaultError(RuntimeError):
    """Raised when credential encryption or decryption cannot be performed."""


def _fernet(key: str | bytes | None = None) -> Fernet:
    raw = key if key is not None else os.getenv(_ENV_KEY)
    if isinstance(raw, str):
        raw = raw.encode("ascii", errors="strict")
    if not raw:
        raise CredentialVaultError(f"{_ENV_KEY} is not configured")
    try:
        return Fernet(raw)
    except (TypeError, ValueError) as exc:
        raise CredentialVaultError(
            f"{_ENV_KEY} must be a valid Fernet key; generate one with Fernet.generate_key()"
        ) from exc


def encrypt_credentials(payload: dict[str, Any], *, key: str | bytes | None = None) -> str:
    """Encrypt a JSON-serializable credential object and return a versioned envelope."""
    if not isinstance(payload, dict) or not payload:
        raise ValueError("Credential payload must be a non-empty object")
    try:
        plaintext = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ValueError("Credential payload must contain JSON-compatible values") from exc
    return _PREFIX + _fernet(key).encrypt(plaintext).decode("ascii")


def decrypt_credentials(envelope: str, *, key: str | bytes | None = None) -> dict[str, Any]:
    """Decrypt a versioned credential envelope; never return partial data."""
    if not isinstance(envelope, str) or not envelope.startswith(_PREFIX):
        raise CredentialVaultError("Unsupported or malformed credential envelope")
    token = envelope[len(_PREFIX):]
    try:
        plaintext = _fernet(key).decrypt(token.encode("ascii"))
        payload = json.loads(plaintext.decode("utf-8"))
    except InvalidToken as exc:
        raise CredentialVaultError("Credential envelope authentication failed") from exc
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise CredentialVaultError("Credential envelope is malformed") from exc
    if not isinstance(payload, dict) or not payload:
        raise CredentialVaultError("Decrypted credential payload is not a non-empty object")
    return payload
