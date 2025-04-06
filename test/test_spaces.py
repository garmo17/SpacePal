import pytest
from unittest.mock import patch, AsyncMock
from backend.api.schemas.spaces import SpaceRead

@pytest.mark.asyncio
async def test_get_spaces_success(async_client):
    fake_spaces = [
        SpaceRead(name="Living Room", description="Nice space", image="http://test.com/img1.jpg", id="1"),
        SpaceRead(name="Kitchen", description="Cooking area", image="http://test.com/img2.jpg", id="2"),
    ]

    with patch("backend.api.services.spaces.list_spaces", return_value=fake_spaces):
        response = await async_client.get("/api/v1/spaces/")

    assert response.status_code == 200
    assert response.json() == [
        {"name": "Living Room", "description": "Nice space", "image": "http://test.com/img1.jpg", "id": "1"},
        {"name": "Kitchen", "description": "Cooking area", "image": "http://test.com/img2.jpg", "id": "2"},
    ]

@pytest.mark.asyncio
async def test_get_space_by_id(async_client):
    fake_space = SpaceRead(
        name="Studio",
        description="Compact and minimal",
        image="http://test.com/studio.jpg",
        id="studio123"
    )

    with patch("backend.api.services.spaces.get_space", return_value=fake_space):
        response = await async_client.get("/api/v1/spaces/studio123")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Studio",
        "description": "Compact and minimal",
        "image": "http://test.com/studio.jpg",
        "id": "studio123"
    }

@pytest.mark.asyncio
async def test_get_space_not_found(async_client):
    with patch("backend.api.services.spaces.get_space", return_value=None):
        response = await async_client.get("/api/v1/spaces/nonexistent")

    assert response.status_code == 404
    assert response.json()["detail"] == "Space not found"

@pytest.mark.asyncio
async def test_create_space_success(async_client, override_is_admin):
    space_data = {
        "name": "Office",
        "description": "Work area",
        "image": "http://test.com/office.jpg"
    }

    created_space = SpaceRead(**space_data, id="space123")

    with patch("backend.api.services.spaces.create_space", return_value=created_space):
        response = await async_client.post("/api/v1/spaces/", json=space_data)

    assert response.status_code == 201
    assert response.json() == {
        "name": "Office",
        "description": "Work area",
        "image": "http://test.com/office.jpg",
        "id": "space123"
    }

@pytest.mark.asyncio
async def test_create_space_conflict(async_client, override_is_admin):
    space_data = {
        "name": "Living Room",
        "description": "Duplicate name",
        "image": "http://test.com/img.jpg"
    }

    with patch("backend.api.services.spaces.create_space", return_value=None):
        response = await async_client.post("/api/v1/spaces/", json=space_data)

    assert response.status_code == 409
    assert response.json()["detail"] == "Space already exists"

@pytest.mark.asyncio
async def test_update_space_success(async_client, override_is_admin):
    update_data = {
        "description": "Updated description"
    }

    updated_space = SpaceRead(
        name="Living Room",
        description="Updated description",
        image="http://test.com/living.jpg",
        id="space123"
    )

    with patch("backend.api.services.spaces.update_space", return_value=updated_space):
        response = await async_client.put("/api/v1/spaces/space123", json=update_data)

    assert response.status_code == 200
    assert response.json() == {
        "name": "Living Room",
        "description": "Updated description",
        "image": "http://test.com/living.jpg",
        "id": "space123"
    }

@pytest.mark.asyncio
async def test_update_space_not_found(async_client, override_is_admin):
    update_data = {"description": "Updated"}

    with patch("backend.api.services.spaces.update_space", return_value=None):
        response = await async_client.put("/api/v1/spaces/invalid_id", json=update_data)

    assert response.status_code == 404
    assert response.json()["detail"] == "Space not found"

@pytest.mark.asyncio
async def test_delete_space_success(async_client, override_is_admin):
    with patch("backend.api.services.spaces.delete_space", return_value=True):
        response = await async_client.delete("/api/v1/spaces/space123")

    assert response.status_code == 200
    assert response.json() == {"message": "Space deleted successfully"}

@pytest.mark.asyncio
async def test_delete_space_not_found(async_client, override_is_admin):
    with patch("backend.api.services.spaces.delete_space", return_value=None):
        response = await async_client.delete("/api/v1/spaces/invalid_id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Space not found"
