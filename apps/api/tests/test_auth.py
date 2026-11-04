from aimn_api.security import SESSION_COOKIE, issue_session, session_email


def test_owner_login_sets_secure_http_only_same_site_cookie(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "OWNER@example.test", "password": "unit-test-password"},
    )
    assert response.status_code == 200
    assert response.json() == {"authenticated": True, "email": "owner@example.test"}
    cookie = response.headers["set-cookie"].lower()
    assert f"{SESSION_COOKIE}=" in cookie
    assert "httponly" in cookie
    assert "samesite=strict" in cookie
    assert "secure" not in cookie  # The test fixture explicitly uses local HTTP.
    assert client.get("/api/v1/auth/me").json() == {
        "authenticated": True,
        "email": "owner@example.test",
    }


def test_owner_session_authorizes_dashboard_api_without_machine_key(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.test", "password": "unit-test-password"},
    )
    assert login.status_code == 200
    assert client.get("/api/v1/networks").status_code == 200


def test_invalid_owner_password_does_not_create_session(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.test", "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert client.get("/api/v1/auth/me").status_code == 401


def test_logout_clears_owner_session(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "owner@example.test", "password": "unit-test-password"},
    )
    assert login.status_code == 200
    logout = client.post("/api/v1/auth/logout")
    assert logout.status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401


def test_session_signature_tampering_is_rejected():
    token = issue_session(
        "owner@example.test",
        "unit-test-signing-secret-32-characters-long",
        3600,
    )
    assert session_email(token, "unit-test-signing-secret-32-characters-long") == "owner@example.test"
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    assert session_email(tampered, "unit-test-signing-secret-32-characters-long") is None
