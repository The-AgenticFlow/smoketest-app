import pytest


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.anyio
async def test_create_task(client):
    resp = await client.post("/api/v1/tasks", json={"title": "Write tests", "priority": "high"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Write tests"
    assert data["priority"] == "high"
    assert data["completed"] is False


@pytest.mark.anyio
async def test_list_tasks(client):
    await client.post("/api/v1/tasks", json={"title": "Task A"})
    await client.post("/api/v1/tasks", json={"title": "Task B"})
    resp = await client.get("/api/v1/tasks")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.anyio
async def test_get_task(client):
    create = await client.post("/api/v1/tasks", json={"title": "Find me"})
    task_id = create.json()["id"]
    resp = await client.get(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Find me"


@pytest.mark.anyio
async def test_update_task(client):
    create = await client.post("/api/v1/tasks", json={"title": "Original"})
    task_id = create.json()["id"]
    resp = await client.patch(f"/api/v1/tasks/{task_id}", json={"completed": True})
    assert resp.status_code == 200
    assert resp.json()["completed"] is True


@pytest.mark.anyio
async def test_delete_task(client):
    create = await client.post("/api/v1/tasks", json={"title": "Delete me"})
    task_id = create.json()["id"]
    resp = await client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204
    resp = await client.get(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 404


@pytest.mark.anyio
async def test_404_task(client):
    resp = await client.get("/api/v1/tasks/9999")
    assert resp.status_code == 404
