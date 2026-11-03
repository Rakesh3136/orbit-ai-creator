import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    database_url: str
    admin_api_key: str | None
    owner_email: str | None
    owner_password_hash: str | None
    session_secret: str | None
    session_ttl_seconds: int
    session_cookie_secure: bool
    web_origin: str

    @classmethod
    def from_env(cls):
        return cls(
            database_url=os.getenv('DATABASE_URL', 'sqlite:///./aimn-dev.db'),
            admin_api_key=os.getenv('AIMN_ADMIN_API_KEY') or None,
            owner_email=os.getenv('AIMN_OWNER_EMAIL') or None,
            owner_password_hash=os.getenv('AIMN_OWNER_PASSWORD_HASH') or None,
            session_secret=os.getenv('AIMN_SESSION_SECRET') or None,
            session_ttl_seconds=max(300, int(os.getenv('AIMN_SESSION_TTL_SECONDS', '43200'))),
            session_cookie_secure=os.getenv('AIMN_SESSION_COOKIE_SECURE', 'true').lower() == 'true',
            web_origin=os.getenv('AIMN_WEB_ORIGIN', 'http://localhost:3000'),
        )

settings = Settings.from_env()