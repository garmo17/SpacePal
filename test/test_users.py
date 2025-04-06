from unittest.mock import AsyncMock
import pytest
from backend.api.db.database import users_collection

@pytest.mark.asyncio
async def test_create_user_success(mocker):
    mock_collection = AsyncMock()
    mock_collection.insert_one.return_value.inserted_id = "fake_id"
    
    mocker.patch("backend.api.db.database.users_collection", mock_collection)
    
    user_id = await create_user("Alice", "alice@example.com")
    
    assert user_id == "fake_id"
    mock_collection.insert_one.assert_awaited_once()

