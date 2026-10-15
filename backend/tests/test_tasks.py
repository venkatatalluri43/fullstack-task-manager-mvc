def test_create_task(client, auth_headers):
    resp = client.post(
        "/api/tasks",
        json={"title": "Write report", "description": "Q3 summary"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    task = resp.get_json()["task"]
    assert task["title"] == "Write report"
    assert task["status"] == "pending"
    assert task["owner"] == "alice"


def test_create_task_requires_title(client, auth_headers):
    resp = client.post("/api/tasks", json={"description": "no title"}, headers=auth_headers)
    assert resp.status_code == 400


def test_create_task_requires_auth(client):
    resp = client.post("/api/tasks", json={"title": "No auth"})
    assert resp.status_code == 401


def test_list_tasks_scoped_to_user(client, auth_headers):
    client.post("/api/tasks", json={"title": "Task A"}, headers=auth_headers)

    client.post("/api/auth/register", json={"username": "carl", "password": "pw12345"})
    carl_login = client.post("/api/auth/login", json={"username": "carl", "password": "pw12345"})
    carl_headers = {"Authorization": f"Bearer {carl_login.get_json()['token']}"}
    client.post("/api/tasks", json={"title": "Task B"}, headers=carl_headers)

    resp = client.get("/api/tasks", headers=auth_headers)
    titles = [t["title"] for t in resp.get_json()["tasks"]]
    assert titles == ["Task A"]

    resp_all = client.get("/api/tasks?scope=all", headers=auth_headers)
    all_titles = {t["title"] for t in resp_all.get_json()["tasks"]}
    assert all_titles == {"Task A", "Task B"}


def test_update_task(client, auth_headers):
    created = client.post("/api/tasks", json={"title": "Old title"}, headers=auth_headers)
    task_id = created.get_json()["task"]["id"]

    resp = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "New title", "status": "in_progress"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    task = resp.get_json()["task"]
    assert task["title"] == "New title"
    assert task["status"] == "in_progress"


def test_update_task_invalid_status(client, auth_headers):
    created = client.post("/api/tasks", json={"title": "Task"}, headers=auth_headers)
    task_id = created.get_json()["task"]["id"]
    resp = client.put(f"/api/tasks/{task_id}", json={"status": "bogus"}, headers=auth_headers)
    assert resp.status_code == 400


def test_update_task_wrong_owner(client, auth_headers):
    created = client.post("/api/tasks", json={"title": "Task"}, headers=auth_headers)
    task_id = created.get_json()["task"]["id"]

    client.post("/api/auth/register", json={"username": "dave", "password": "pw12345"})
    dave_login = client.post("/api/auth/login", json={"username": "dave", "password": "pw12345"})
    dave_headers = {"Authorization": f"Bearer {dave_login.get_json()['token']}"}

    resp = client.put(f"/api/tasks/{task_id}", json={"title": "Hacked"}, headers=dave_headers)
    assert resp.status_code == 403


def test_delete_task(client, auth_headers):
    created = client.post("/api/tasks", json={"title": "Temp"}, headers=auth_headers)
    task_id = created.get_json()["task"]["id"]

    resp = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 204

    resp_get = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert resp_get.status_code == 404


def test_get_nonexistent_task(client, auth_headers):
    resp = client.get("/api/tasks/9999", headers=auth_headers)
    assert resp.status_code == 404
