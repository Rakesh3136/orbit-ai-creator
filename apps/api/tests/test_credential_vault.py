import pytest
from cryptography.fernet import Fernet

from aimn_api.credential_vault import (
    CredentialVaultError,
    decrypt_credentials,
    encrypt_credentials,
)


def test_credentials_round_trip_without_exposing_plaintext():
    key = Fernet.generate_key()
    payload = {"refresh_token": "never-print-this", "token_uri": "https://oauth2.googleapis.com/token"}
    envelope = encrypt_credentials(payload, key=key)
    assert envelope.startswith("aimn:v1:")
    assert "never-print-this" not in envelope
    assert decrypt_credentials(envelope, key=key) == payload


def test_missing_key_fails_closed(monkeypatch):
    monkeypatch.delenv("AIMN_CREDENTIAL_ENCRYPTION_KEY", raising=False)
    with pytest.raises(CredentialVaultError, match="not configured"):
        encrypt_credentials({"refresh_token": "secret"})


def test_wrong_key_cannot_decrypt_credentials():
    envelope = encrypt_credentials({"refresh_token": "secret"}, key=Fernet.generate_key())
    with pytest.raises(CredentialVaultError, match="authentication failed"):
        decrypt_credentials(envelope, key=Fernet.generate_key())


@pytest.mark.parametrize("payload", [{}, [], None, "token"])
def test_invalid_payload_is_rejected(payload):
    with pytest.raises(ValueError):
        encrypt_credentials(payload)


def test_unknown_envelope_version_is_rejected():
    with pytest.raises(CredentialVaultError, match="Unsupported"):
        decrypt_credentials("aimn:v2:abc", key=Fernet.generate_key())
