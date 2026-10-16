def test_create_task(client, auth_headers, project_id):
    resp = client.post(
        "/api/tasks",
        json={
            "title": "Write report",
            "description": "Q3 summary",
            "project_id": project_id,
            "priority": "high",
            "due_date": "2026-12-01",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    task = resp.get_json()["task"]
    assert task["title"] == "Write report"
    assert task["status"] == "pending"
    assert task["priority"] == "high"
    assert task["due_date"] == "2026-12-01"
    assert task["owner"] == "alice"
    assert task["assignee"] == "alice"  # defaults to creator


def test_create_task_requires_title(client, auth_headers, project_id):
    resp = client.post(
        "/api/tasks", json={"description": "no title", "project_id": project_id}, headers=auth_headers
    )
    assert resp.status_code == 400


def test_create_task_requires_project(client, auth_headers):
    resp = client.post("/api/tasks", json={"title": "No project"}, headers=auth_headers)
    assert resp.status_code == 404


def test_create_task_requires_auth(client, project_id):
    resp = client.post("/api/tasks", json={"title": "No auth", "project_id": project_id})
    assert resp.status_code == 401


def test_create_task_invalid_due_date(client, auth_headers, project_id):
    resp = client.post(
        "/api/tasks",
        json={"title": "Bad date", "project_id": project_id, "due_date": "not-a-date"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_assign_task_to_teammate(client, auth_headers, project_id):
    client.post("/api/auth/register", json={"username": "bob", "password": "pw12345"})
    users = client.get("/api/users", headers=auth_headers).get_json()["users"]
    bob_id = next(u["id"] for u in users if u["username"] == "bob")

    created = client.post(
        "/api/tasks",
        json={"title": "Assigned task", "project_id": project_id, "assignee_id": bob_id},
        headers=auth_headers,
    )
    assert created.status_code == 201
    assert created.get_json()["task"]["assignee"] == "bob"


def test_assignee_can_update_status_only(client, auth_headers, project_id):
    client.post("/api/auth/register", json={"username": "bob", "password": "pw12345"})
    bob_login = client.post("/api/auth/login", json={"username": "bob", "password": "pw12345"})
    bob_headers = {"Authorization": f"Bearer {bob_login.get_json()['token']}"}
    users = client.get("/api/users", headers=auth_headers).get_json()["users"]
    bob_id = next(u["id"] for u in users if u["username"] == "bob")

    created = client.post(
        "/api/tasks",
        json={"title": "Assigned task", "project_id": project_id, "assignee_id": bob_id},
        headers=auth_headers,
    )
    task_id = created.get_json()["task"]["id"]

    status_resp = client.put(f"/api/tasks/{task_id}", json={"status": "done"}, headers=bob_headers)
    assert status_resp.status_code == 200
    assert status_resp.get_json()["task"]["status"] == "done"

    title_resp = client.put(f"/api/tasks/{task_id}", json={"title": "Hacked"}, headers=bob_headers)
    assert title_resp.status_code == 403


def test_list_tasks_scoped_to_user(client, auth_headers, project_id):
    client.post("/api/tasks", json={"title": "Task A", "project_id": project_id}, headers=auth_headers)

    client.post("/api/auth/register", json={"username": "carl", "password": "pw12345"})
    carl_login = client.post("/api/auth/login", json={"username": "carl", "password": "pw12345"})
    carl_headers = {"Authorization": f"Bearer {carl_login.get_json()['token']}"}
    carl_project = client.post("/api/projects", json={"name": "Carl Project"}, headers=carl_headers)
    carl_project_id = carl_project.get_json()["project"]["id"]
    client.post("/api/tasks", json={"title": "Task B", "project_id": carl_project_id}, headers=carl_headers)

    resp = client.get("/api/tasks", headers=auth_headers)
    titles = [t["title"] for t in resp.get_json()["tasks"]]
    assert titles == ["Task A"]

    resp_all = client.get("/api/tasks?scope=all", headers=auth_headers)
    all_titles = {t["title"] for t in resp_all.get_json()["tasks"]}
    assert all_titles == {"Task A", "Task B"}


def test_list_tasks_filtered_by_project(client, auth_headers, project_id):
    other_project = client.post("/api/projects", json={"name": "Other"}, headers=auth_headers)
    other_project_id = other_project.get_json()["project"]["id"]

    client.post("/api/tasks", json={"title": "In project", "project_id": project_id}, headers=auth_headers)
    client.post("/api/tasks", json={"title": "In other", "project_id": other_project_id}, headers=auth_headers)

    resp = client.get(f"/api/tasks?scope=all&project_id={project_id}", headers=auth_headers)
    titles = [t["title"] for t in resp.get_json()["tasks"]]
    assert titles == ["In project"]


def test_update_task(client, auth_headers, project_id):
    created = client.post(
        "/api/tasks", json={"title": "Old title", "project_id": project_id}, headers=auth_headers
    )
    task_id = created.get_json()["task"]["id"]

    resp = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "New title", "status": "in_progress", "priority": "low"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    task = resp.get_json()["task"]
    assert task["title"] == "New title"
    assert task["status"] == "in_progress"
    assert task["priority"] == "low"


def test_update_task_invalid_status(client, auth_headers, project_id):
    created = client.post("/api/tasks", json={"title": "Task", "project_id": project_id}, headers=auth_headers)
    task_id = created.get_json()["task"]["id"]
    resp = client.put(f"/api/tasks/{task_id}", json={"status": "bogus"}, headers=auth_headers)
    assert resp.status_code == 400


def test_update_task_wrong_owner(client, auth_headers, project_id):
    created = client.post("/api/tasks", json={"title": "Task", "project_id": project_id}, headers=auth_headers)
    task_id = created.get_json()["task"]["id"]

    client.post("/api/auth/register", json={"username": "dave", "password": "pw12345"})
    dave_login = client.post("/api/auth/login", json={"username": "dave", "password": "pw12345"})
    dave_headers = {"Authorization": f"Bearer {dave_login.get_json()['token']}"}

    resp = client.put(f"/api/tasks/{task_id}", json={"title": "Hacked"}, headers=dave_headers)
    assert resp.status_code == 403


def test_delete_task(client, auth_headers, project_id):
    created = client.post("/api/tasks", json={"title": "Temp", "project_id": project_id}, headers=auth_headers)
    task_id = created.get_json()["task"]["id"]

    resp = client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert resp.status_code == 204

    resp_get = client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert resp_get.status_code == 404


def test_get_nonexistent_task(client, auth_headers):
    resp = client.get("/api/tasks/9999", headers=auth_headers)
    assert resp.status_code == 404
