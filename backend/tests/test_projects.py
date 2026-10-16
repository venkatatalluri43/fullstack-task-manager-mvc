def test_create_project(client, auth_headers):
    resp = client.post(
        "/api/projects",
        json={"name": "Launch Plan", "description": "Q4 launch"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    project = resp.get_json()["project"]
    assert project["name"] == "Launch Plan"
    assert project["owner"] == "alice"
    assert project["task_count"] == 0


def test_create_project_requires_name(client, auth_headers):
    resp = client.post("/api/projects", json={"description": "no name"}, headers=auth_headers)
    assert resp.status_code == 400


def test_create_project_requires_auth(client):
    resp = client.post("/api/projects", json={"name": "No auth"})
    assert resp.status_code == 401


def test_list_projects_scoped_to_user(client, auth_headers):
    client.post("/api/projects", json={"name": "Alice Project"}, headers=auth_headers)

    client.post("/api/auth/register", json={"username": "carl", "password": "pw12345"})
    carl_login = client.post("/api/auth/login", json={"username": "carl", "password": "pw12345"})
    carl_headers = {"Authorization": f"Bearer {carl_login.get_json()['token']}"}
    client.post("/api/projects", json={"name": "Carl Project"}, headers=carl_headers)

    resp = client.get("/api/projects", headers=auth_headers)
    names = [p["name"] for p in resp.get_json()["projects"]]
    assert names == ["Alice Project"]


def test_update_project(client, auth_headers, project_id):
    resp = client.put(
        f"/api/projects/{project_id}",
        json={"name": "Renamed", "description": "updated"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.get_json()["project"]["name"] == "Renamed"


def test_update_project_wrong_owner(client, auth_headers, project_id):
    client.post("/api/auth/register", json={"username": "dave", "password": "pw12345"})
    dave_login = client.post("/api/auth/login", json={"username": "dave", "password": "pw12345"})
    dave_headers = {"Authorization": f"Bearer {dave_login.get_json()['token']}"}

    resp = client.put(f"/api/projects/{project_id}", json={"name": "Hacked"}, headers=dave_headers)
    assert resp.status_code == 403


def test_delete_project_cascades_tasks(client, auth_headers, project_id):
    client.post(
        "/api/tasks",
        json={"title": "Task A", "project_id": project_id},
        headers=auth_headers,
    )
    resp = client.delete(f"/api/projects/{project_id}", headers=auth_headers)
    assert resp.status_code == 204

    resp_get = client.get(f"/api/projects/{project_id}", headers=auth_headers)
    assert resp_get.status_code == 404


def test_get_nonexistent_project(client, auth_headers):
    resp = client.get("/api/projects/9999", headers=auth_headers)
    assert resp.status_code == 404
