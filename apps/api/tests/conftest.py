import base64
import hashlib
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
    test_engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    sessions = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)
    def override_db():
        db = sessions()
        try:
            yield db
        finally:
            db.close()
    salt = 'aimn-unit-test-salt'
    digest = hashlib.pbkdf2_hmac('sha256', b'unit-test-password', salt.encode(), 310000)
    encoded = base64.urlsafe_b64encode(digest).decode().rstrip('=')
    password_hash = 'pbkdf2_sha256$310000$' + salt + '$' + encoded
    monkeypatch.setattr(security, 'settings', SimpleNamespace(
        admin_api_key='test-only-key', owner_email='owner@example.test',
        owner_password_hash=password_hash, session_secret='unit-test-signing-secret-32-characters-long',
        session_ttl_seconds=3600, session_cookie_secure=False
    ))
    app.state.test_sessions = sessions
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    if hasattr(app.state, "test_sessions"):
        del app.state.test_sessions
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()

@pytest.fixture()
def auth_headers():
    return {'X-AIMN-API-Key': 'test-only-key'}