from datetime import datetime
from uuid import UUID

import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from litestar.testing import AsyncTestClient


@pytest.mark.asyncio(scope="session")
async def test_post(client: AsyncTestClient) -> None:
    """Test if POST /tasks returns correct response."""

    operation = {"type": "test", "parameters": {}}
    condition = {"type": "now", "parameters": {}}
    dependencies = {}

    response = await client.post(
        "/tasks",
        json={
            "operation": operation,
            "condition": condition,
            "dependencies": dependencies,
        },
    )

    assert response.status_code == HTTP_201_CREATED

    data = response.json()
    assert "task" in data
    assert "scheduled" in data

    task = data["task"]
    assert isinstance(task, dict)
    assert "id" in task
    assert "operation" in task
    assert "condition" in task
    assert "dependencies" in task

    tid = task["id"]
    assert isinstance(tid, str)
    assert UUID(tid)

    toperation = task["operation"]
    assert isinstance(toperation, dict)
    assert toperation == operation

    tcondition = task["condition"]
    assert isinstance(tcondition, dict)
    assert tcondition == condition

    tdependencies = task["dependencies"]
    assert isinstance(tdependencies, dict)
    assert tdependencies == dependencies

    scheduled = data["scheduled"]
    assert isinstance(scheduled, str)
    assert datetime.fromisoformat(scheduled)


@pytest.mark.asyncio(scope="session")
async def test_get(client: AsyncTestClient) -> None:
    """Test if GET /tasks returns correct response."""

    response = await client.post(
        "/tasks",
        json={
            "operation": {"type": "test", "parameters": {}},
            "condition": {"type": "now", "parameters": {}},
            "dependencies": {},
        },
    )
    id = response.json()["task"]["id"]

    response = await client.get("/tasks")

    assert response.status_code == HTTP_200_OK

    data = response.json()
    assert "pending" in data
    assert "running" in data
    assert "cancelled" in data
    assert "failed" in data
    assert "completed" in data

    pending = data["pending"]
    assert isinstance(pending, list)

    running = data["running"]
    assert isinstance(running, list)

    cancelled = data["cancelled"]
    assert isinstance(cancelled, list)

    failed = data["failed"]
    assert isinstance(failed, list)

    completed = data["completed"]
    assert isinstance(completed, list)

    all = pending + running + cancelled + failed + completed
    assert id in all


@pytest.mark.asyncio(scope="session")
async def test_get_by_id(client: AsyncTestClient) -> None:
    """Test if GET /tasks/{id} returns correct response."""

    operation = {"type": "test", "parameters": {}}
    condition = {"type": "now", "parameters": {}}
    dependencies = {}

    response = await client.post(
        "/tasks",
        json={
            "operation": operation,
            "condition": condition,
            "dependencies": dependencies,
        },
    )
    id = response.json()["task"]["id"]

    response = await client.get(f"/tasks/{id}")

    assert response.status_code == HTTP_200_OK

    data = response.json()
    assert "task" in data
    assert "status" in data

    task = data["task"]
    assert isinstance(task, dict)
    assert "id" in task
    assert "operation" in task
    assert "condition" in task
    assert "dependencies" in task

    tid = task["id"]
    assert isinstance(tid, str)
    assert UUID(tid)
    assert tid == id

    toperation = task["operation"]
    assert isinstance(toperation, dict)
    assert toperation == operation

    tcondition = task["condition"]
    assert isinstance(tcondition, dict)
    assert tcondition == condition

    tdependencies = task["dependencies"]
    assert isinstance(tdependencies, dict)
    assert tdependencies == dependencies

    status = data["status"]
    assert isinstance(status, str)
    assert status in {"pending", "running", "cancelled", "failed", "completed"}
