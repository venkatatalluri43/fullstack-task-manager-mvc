def test_register_success(client):
    resp = client.post("/api/auth/register", json={"username": "bob", "password": "pw12345"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["user"]["username"] == "bob"
    assert "token" in data


def test_register_duplicate_username(client):
    client.post("/api/auth/register", json={"username": "bob", "password": "pw12345"})
    resp = client.post("/api/auth/register", json={"username": "bob", "password": "pw12345"})
    assert resp.status_code == 409


def test_register_missing_fields(client):
    resp = client.post("/api/auth/register", json={"username": "bob"})
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/api/auth/register", json={"username": "bob", "password": "pw12345"})
    resp = client.post("/api/auth/login", json={"username": "bob", "password": "pw12345"})
    assert resp.status_code == 200
    assert "token" in resp.get_json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={"username": "bob", "password": "pw12345"})
    resp = client.post("/api/auth/login", json={"username": "bob", "password": "wrong"})
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post("/api/auth/login", json={"username": "ghost", "password": "pw12345"})
    assert resp.status_code == 401
