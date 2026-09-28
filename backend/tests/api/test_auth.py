def test_register_login_me_and_refresh(client):
    registered = client.post("/api/v1/auth/register", json={"email": "aya@example.com", "username": "aya_ci", "password": "very-safe-password"})
    assert registered.status_code == 201
    data = registered.json()
    assert data["user"]["role"] == "USER"
    assert client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {data['access_token']}"}).status_code == 200
    login = client.post("/api/v1/auth/login", json={"email": "AYA@example.com", "password": "very-safe-password"})
    assert login.status_code == 200
    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": login.json()["refresh_token"]})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]
def test_auth_rejects_weak_password_duplicate_and_bad_token(client):
    weak = client.post("/api/v1/auth/register", json={"email": "bad@example.com", "username": "bad_user", "password": "short"})
    assert weak.status_code == 422
    body = {"email": "aya@example.com", "username": "aya_ci", "password": "very-safe-password"}
    assert client.post("/api/v1/auth/register", json=body).status_code == 201
    assert client.post("/api/v1/auth/register", json=body).status_code == 409
    assert client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid"}).status_code == 401


def test_logout_invalidates_current_tokens(client):
    registered = client.post("/api/v1/auth/register", json={"email": "logout@example.com", "username": "logout_user", "password": "very-safe-password"})
    tokens = registered.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    assert client.post("/api/v1/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/v1/auth/me", headers=headers).status_code == 401
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401
