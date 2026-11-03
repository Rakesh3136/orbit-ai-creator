import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    database_url: str
    admin_api_key: str | None

    @classmethod
    def from_env(cls):
        return cls(
            database_url=os.getenv("DATABASE_URL", "sqlite:///./aimn-dev.db"),
            admin_api_key=os.getenv("AIMN_ADMIN_API_KEY") or None,
        )

settings = Settings.from_env()
