import pytest
from httpx import AsyncClient
from backend.api.schemas.users import UserRead
from backend.api.models.users import UserDB
from unittest.mock import patch

@pytest.mark.asyncio
async def test_get_user_me(async_client, override_get_current_user):
    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer faketoken"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "username": "mockuser",
        "email": "mock@example.com",
        "id": "user123"
    }

@pytest.mark.asyncio
async def test_get_users_list(async_client, override_is_admin):
    fake_users = [
        UserRead(username="admin", email="admin@example.com", id="1"),
        UserRead(username="user1", email="user1@example.com", id="2"),
    ]

    with patch("backend.api.services.users.list_users", return_value=fake_users):
        response = await async_client.get("/api/v1/users/")

    assert response.status_code == 200
    assert response.json() == [
        {"username": "admin", "email": "admin@example.com", "id": "1"},
        {"username": "user1", "email": "user1@example.com", "id": "2"},
    ]

@pytest.mark.asyncio
async def test_get_user_by_id(async_client, override_is_admin):
    fake_user = UserRead(username="targetuser", email="target@example.com", id="abc123")

    with patch("backend.api.services.users.get_user", return_value=fake_user):
        response = await async_client.get("/api/v1/users/abc123")

    assert response.status_code == 200
    assert response.json() == {
        "username": "targetuser",
        "email": "target@example.com",
        "id": "abc123"
    }

@pytest.mark.asyncio
async def test_create_user(async_client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword"
    }

    fake_user = UserRead(**user_data, id="fakeid123")

    with patch("backend.api.services.users.create_user", return_value=fake_user):
        response = await async_client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 201
    assert response.json() == {
        "username": "newuser",
        "email": "newuser@example.com",
        "id": "fakeid123"
    }

@pytest.mark.asyncio
async def test_create_user_conflict(async_client):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "somepass"
    }

    with patch("backend.api.services.users.create_user", return_value=None):
        response = await async_client.post("/api/v1/users/", json=user_data)

    assert response.status_code == 409
    assert response.json()["detail"] == "User already exists"

@pytest.mark.asyncio
async def test_update_own_user(async_client, override_get_current_user):
    updated_user = UserRead(username="mockuser", email="mock_new@example.com", id="user123")

    with patch("backend.api.services.users.update_user", return_value=updated_user):
        response = await async_client.put("/api/v1/users/user123", json={"email": "mock_new@example.com"})

    assert response.status_code == 200
    assert response.json() == {
        "username": "mockuser",
        "email": "mock_new@example.com",
        "id": "user123"
    }

@pytest.mark.asyncio
async def test_update_other_user_forbidden(async_client, override_get_current_user):
    fake_other_user = UserDB(
        username="someone_else",
        email="other@example.com",
        password="otherpass",
        _id="other_id"
    )

    with patch("backend.api.services.users.get_user", return_value=fake_other_user):
        response = await async_client.put(
            "/api/v1/users/other_id",
            json={"email": "not_allowed@example.com"}
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "You can only update your own user"

@pytest.mark.asyncio
async def test_delete_user_by_id(async_client, override_is_admin):
    with patch("backend.api.services.users.delete_user", return_value=True):
        response = await async_client.delete("/api/v1/users/abc123")

    assert response.status_code == 200
    assert response.json() == {"message": "User deleted successfully"}

@pytest.mark.asyncio
async def test_delete_user_not_found(async_client, override_is_admin):
    with patch("backend.api.services.users.delete_user", return_value=None):
        response = await async_client.delete("/api/v1/users/nonexistent")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_delete_all_users_success(async_client, override_is_admin):
    with patch("backend.api.services.users.delete_all_users", return_value=3):
        response = await async_client.delete("/api/v1/users/")

    assert response.status_code == 200
    assert response.json() == {"message": "Deleted 3 users"}

@pytest.mark.asyncio
async def test_delete_all_users_not_found(async_client, override_is_admin):
    with patch("backend.api.services.users.delete_all_users", return_value=0):
        response = await async_client.delete("/api/v1/users/")

    assert response.status_code == 404
    assert response.json()["detail"] == "No users found to delete"
