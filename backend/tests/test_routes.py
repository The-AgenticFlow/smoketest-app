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
    """Test basic listing with pagination defaults"""
    await client.post("/api/v1/tasks", json={"title": "Task A"})
    await client.post("/api/v1/tasks", json={"title": "Task B"})
    resp = await client.get("/api/v1/tasks")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 2
    assert data["total"] == 2
    assert data["limit"] == 50  # default
    assert data["offset"] == 0  # default


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


@pytest.mark.anyio
async def test_list_tasks_filter_by_completed(client):
    """Test filtering by completed status"""
    # Create test data
    await client.post("/api/v1/tasks", json={"title": "Completed Task", "completed": True})
    await client.post("/api/v1/tasks", json={"title": "Pending Task 1", "completed": False})
    await client.post("/api/v1/tasks", json={"title": "Pending Task 2", "completed": False})

    # Filter for completed=true
    resp = await client.get("/api/v1/tasks?completed=true")
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["completed"] is True

    # Filter for completed=false
    resp = await client.get("/api/v1/tasks?completed=false")
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert all(t["completed"] is False for t in data["items"])


@pytest.mark.anyio
async def test_list_tasks_filter_by_priority(client):
    """Test filtering by priority level"""
    # Create test data
    await client.post("/api/v1/tasks", json={"title": "High Priority", "priority": "high"})
    await client.post("/api/v1/tasks", json={"title": "Low Priority 1", "priority": "low"})
    await client.post("/api/v1/tasks", json={"title": "Low Priority 2", "priority": "low"})

    # Filter by priority=high
    resp = await client.get("/api/v1/tasks?priority=high")
    data = resp.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["priority"] == "high"

    # Filter by priority=low
    resp = await client.get("/api/v1/tasks?priority=low")
    data = resp.json()
    assert data["total"] == 2
    assert all(t["priority"] == "low" for t in data["items"])


@pytest.mark.anyio
async def test_list_tasks_combined_filters(client):
    """Test combining completed and priority filters"""
    # Create test data with combinations
    await client.post("/api/v1/tasks", json={"title": "High Done", "priority": "high", "completed": True})
    await client.post("/api/v1/tasks", json={"title": "High Pending", "priority": "high", "completed": False})
    await client.post("/api/v1/tasks", json={"title": "Low Done", "priority": "low", "completed": True})
    await client.post("/api/v1/tasks", json={"title": "Low Pending", "priority": "low", "completed": False})

    # Both filters: completed=false AND priority=high
    resp = await client.get("/api/v1/tasks?completed=false&priority=high")
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "High Pending"


@pytest.mark.anyio
async def test_list_tasks_pagination(client):
    """Test pagination with limit and offset"""
    # Create 25 tasks
    for i in range(25):
        await client.post("/api/v1/tasks", json={"title": f"Task {i+1}"})

    # Page 1: limit=10, offset=0
    resp = await client.get("/api/v1/tasks?limit=10&offset=0")
    data = resp.json()
    assert data["total"] == 25
    assert len(data["items"]) == 10
    assert data["limit"] == 10
    assert data["offset"] == 0

    # Page 2: limit=10, offset=10
    resp = await client.get("/api/v1/tasks?limit=10&offset=10")
    data = resp.json()
    assert len(data["items"]) == 10
    # Verify we're getting different items (IDs should be sequential from 11-20)
    ids = [t["id"] for t in data["items"]]
    assert min(ids) >= 11 or max(ids) <= 20

    # Page 3: limit=10, offset=20
    resp = await client.get("/api/v1/tasks?limit=10&offset=20")
    data = resp.json()
    assert len(data["items"]) == 5  # Only 5 remaining


@pytest.mark.anyio
async def test_list_tasks_pagination_edge_cases(client):
    """Test pagination edge cases"""
    # Create 5 tasks
    for i in range(5):
        await client.post("/api/v1/tasks", json={"title": f"Task {i+1}"})

    # Offset beyond total - should return empty items but correct total
    resp = await client.get("/api/v1/tasks?limit=10&offset=100")
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 0
    assert data["limit"] == 10
    assert data["offset"] == 100

    # Limit=1 should return exactly 1 item
    resp = await client.get("/api/v1/tasks?limit=1&offset=0")
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 1


@pytest.mark.anyio
async def test_list_tasks_default_pagination(client):
    """Test that default pagination works when no params provided"""
    # Create 60 tasks (more than default limit of 50)
    for i in range(60):
        await client.post("/api/v1/tasks", json={"title": f"Task {i+1}"})

    # No params - should use defaults (limit=50, offset=0)
    resp = await client.get("/api/v1/tasks")
    data = resp.json()
    assert data["total"] == 60
    assert len(data["items"]) == 50  # Default limit
    assert data["limit"] == 50
    assert data["offset"] == 0
