def register(client, username):
    response = client.post("/api/v1/auth/register", json={
        "email": f"{username}@example.ci",
        "username": username,
        "password": "safe-community-passphrase-123",
    })
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_community_persists_posts_comments_and_member_reactions(client):
    owner = register(client, "community_owner")
    member = register(client, "community_member")
    assert client.get("/api/v1/community/posts?page_size=1").status_code == 200
    assert client.post("/api/v1/community/posts", json={"title": "Salut", "content": "Bonjour la communauté"}).status_code == 401

    created = client.post("/api/v1/community/posts", headers=owner, json={"title": "Mon idée", "content": "Construisons un club Python à Bouaké."})
    assert created.status_code == 201, created.text
    post = created.json()
    assert post["username"] == "community_owner"
    post_id = post["id"]

    comment = client.post(f"/api/v1/community/posts/{post_id}/comments", headers=member, json={"content": "Je veux participer."})
    assert comment.status_code == 200
    assert comment.json()["comments"][0]["username"] == "community_member"
    assert comment.json()["comment_count"] == 1

    assert client.put(f"/api/v1/community/posts/{post_id}/reaction").status_code == 401
    first = client.put(f"/api/v1/community/posts/{post_id}/reaction", headers=member)
    second = client.put(f"/api/v1/community/posts/{post_id}/reaction", headers=member)
    assert first.json() == {"reacted": True, "reaction_count": 1}
    assert second.json() == {"reacted": True, "reaction_count": 1}
    assert client.get(f"/api/v1/community/posts/{post_id}", headers=member).json()["viewer_reacted"] is True

    removed = client.delete(f"/api/v1/community/posts/{post_id}/reaction", headers=member)
    assert removed.json() == {"reacted": False, "reaction_count": 0}
    assert client.delete(f"/api/v1/community/posts/{post_id}/reaction", headers=member).json()["reaction_count"] == 0
    page = client.get("/api/v1/community/posts?page=1&page_size=1").json()
    assert page["total"] == 1 and page["items"][0]["comment_count"] == 1


def test_community_validates_empty_content_and_paginates(client):
    headers = register(client, "community_validation")
    assert client.post("/api/v1/community/posts", headers=headers, json={"title": "   ", "content": "not empty"}).status_code == 422
    assert client.post("/api/v1/community/posts", headers=headers, json={"title": "Valid", "content": "  "}).status_code == 422
    assert client.get("/api/v1/community/posts?page=0").status_code == 422
