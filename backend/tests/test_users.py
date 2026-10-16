def test_list_users_requires_auth(client):
    resp = client.get("/api/users")
    assert resp.status_code == 401


def test_list_users(client, auth_headers):
    client.post("/api/auth/register", json={"username": "bob", "password": "pw12345"})
    resp = client.get("/api/users", headers=auth_headers)
    assert resp.status_code == 200
    usernames = {u["username"] for u in resp.get_json()["users"]}
    assert usernames == {"alice", "bob"}
