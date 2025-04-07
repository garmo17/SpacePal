import pytest
from unittest.mock import patch, AsyncMock
from bson import ObjectId
from backend.api.services.users import (
    get_user, create_user, delete_user, update_user, delete_all_users
)
from backend.api.schemas.users import UserCreate, UserUpdate, UserRead
from backend.api.models.users import UserDB


@pytest.mark.asyncio
async def test_get_user_valid_id():
    user_dict = {"_id": ObjectId(), "username": "test", "email": "test@example.com", "password": "hashed"}
    with patch("backend.api.db.database.users_collection.find_one", new=AsyncMock(return_value=user_dict)):
        result = await get_user(str(user_dict["_id"]))
        assert isinstance(result, UserRead)
        assert result.username == "test"


@pytest.mark.asyncio
async def test_get_user_invalid_id():
    result = await get_user("invalid-id")
    assert result is None


@pytest.mark.asyncio
async def test_create_user_already_exists():
    user_data = UserCreate(username="existing", email="exists@example.com", password="1234")
    with patch("backend.api.db.database.users_collection.count_documents", new=AsyncMock(return_value=1)):
        result = await create_user(user_data)
        assert result is None


@pytest.mark.asyncio
async def test_create_user_success():
    user_data = UserCreate(username="new", email="new@example.com", password="1234")
    user_id = ObjectId()
    new_user_dict = {"_id": user_id, "username": "new", "email": "new@example.com", "password": "hashed"}

    with patch("backend.api.db.database.users_collection.count_documents", new=AsyncMock(return_value=0)), \
         patch("backend.api.db.database.users_collection.insert_one", new=AsyncMock(return_value=AsyncMock(inserted_id=user_id))), \
         patch("backend.api.db.database.users_collection.find_one", new=AsyncMock(return_value=new_user_dict)):
        result = await create_user(user_data)
        assert isinstance(result, UserRead)
        assert result.email == "new@example.com"


@pytest.mark.asyncio
async def test_update_user_success():
    user_id = str(ObjectId())
    updated_data = UserUpdate(email="updated@example.com")

    original_user = UserRead(username="test", email="test@example.com", id=user_id)
    updated_user = UserRead(username="test", email="updated@example.com", id=user_id)

    with patch("backend.api.services.users.get_user", side_effect=[original_user, updated_user]), \
         patch("backend.api.db.database.users_collection.update_one", new=AsyncMock()):
        result = await update_user(user_id, updated_data)
        assert result.email == "updated@example.com"


@pytest.mark.asyncio
async def test_update_user_invalid_id():
    result = await update_user("invalid-id", UserUpdate(email="test@test.com"))
    assert result is None


@pytest.mark.asyncio
async def test_delete_user_success():
    user_id = str(ObjectId())
    fake_user = UserRead(username="delete", email="del@example.com", id=user_id)

    with patch("backend.api.services.users.get_user", return_value=fake_user), \
         patch("backend.api.db.database.users_collection.delete_one", new=AsyncMock()):
        result = await delete_user(user_id)
        assert result.username == "delete"


@pytest.mark.asyncio
async def test_delete_user_invalid_id():
    result = await delete_user("invalid-id")
    assert result is None


@pytest.mark.asyncio
async def test_delete_all_users_returns_count():
    mock_delete_result = AsyncMock()
    mock_delete_result.deleted_count = 5
    with patch("backend.api.db.database.users_collection.delete_many", new=AsyncMock(return_value=mock_delete_result)):
        result = await delete_all_users()
        assert result == 5

