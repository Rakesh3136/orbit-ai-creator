import secrets
from fastapi import Header, HTTPException, status
from aimn_api.config import settings

def require_admin_api_key(x_aimn_api_key: str | None = Header(default=None)) -> None:
    expected = settings.admin_api_key
    if not expected:
        raise HTTPException(status_code=503, detail="Management API locked: configure AIMN_ADMIN_API_KEY.")
    if not x_aimn_api_key or not secrets.compare_digest(x_aimn_api_key, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Valid X-AIMN-API-Key required.")
