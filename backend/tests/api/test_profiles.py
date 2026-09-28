def register(client, email="awa@example.ci", username="awa_ci"):
    response = client.post("/api/v1/auth/register", json={
        "email": email,
        "username": username,
        "password": "secure-passphrase-123",
    })
    assert response.status_code == 201
    return response.json()


def test_profile_is_created_and_can_be_updated(client):
    account = register(client)
    headers = {"Authorization": f"Bearer {account['access_token']}"}

    initial = client.get("/api/v1/profile/me", headers=headers)
    assert initial.status_code == 200
    assert initial.json()["display_name"] == "awa_ci"
    assert initial.json()["city"] == "Abidjan"
    assert initial.json()["skills"] == []

    updated = client.put("/api/v1/profile/me", headers=headers, json={
        "display_name": " Awa Kouamé ",
        "bio": "  Je construis des outils numériques.  ",
        "city": " Bouaké ",
        "country": "Côte d’Ivoire",
        "skills": ["Python", " Python ", "Data"],
        "interests": ["Agriculture", "IA"],
    })
    assert updated.status_code == 200
    body = updated.json()
    assert body["display_name"] == "Awa Kouamé"
    assert body["bio"] == "Je construis des outils numériques."
    assert body["city"] == "Bouaké"
    assert body["skills"] == ["Python", "Data"]

    persisted = client.get("/api/v1/profile/me", headers=headers)
    assert persisted.json()["display_name"] == "Awa Kouamé"
    assert persisted.json()["interests"] == ["Agriculture", "IA"]


def test_profile_requires_authentication_and_rejects_invalid_data(client):
    assert client.get("/api/v1/profile/me").status_code == 401
    account = register(client, email="invalid@example.ci", username="invalid_ci")
    headers = {"Authorization": f"Bearer {account['access_token']}"}
    invalid = client.put("/api/v1/profile/me", headers=headers, json={
        "display_name": "",
        "bio": "",
        "city": "Abidjan",
        "country": "Côte d’Ivoire",
        "skills": [],
        "interests": [],
    })
    assert invalid.status_code == 422
