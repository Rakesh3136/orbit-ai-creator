import pytest
from types import SimpleNamespace
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from aimn_api.db import get_db
from aimn_api.main import app
from aimn_api.models import Base
import aimn_api.security as security

@pytest.fixture()
def client(monkeypatch):
    test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    sessions = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)
    def override_db():
        db = sessions()
        try:
            yield db
        finally:
            db.close()
    monkeypatch.setattr(security, "settings", SimpleNamespace(admin_api_key="test-only-key"))
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()

@pytest.fixture()
def auth_headers():
    return {"X-AIMN-API-Key": "test-only-key"}
