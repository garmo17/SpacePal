import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from backend.api.main import app
from unittest.mock import AsyncMock
from backend.api.dependencies.auth import is_admin
from backend.api.services.auth_service import get_current_user
from backend.api.models.users import UserDB
from backend.api.db import database

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    yield client
    await client.aclose()

@pytest_asyncio.fixture
async def override_is_admin():
    app.dependency_overrides[is_admin] = lambda: AsyncMock()
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def override_get_current_user():
    fake_user = UserDB(
        username="mockuser",
        email="mock@example.com",
        password="hashed",
        _id="user123"
    )
    app.dependency_overrides[get_current_user] = lambda: fake_user
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
@pytest_asyncio.fixture(autouse=True)
def mock_database_collections(monkeypatch):
    mock_collection = AsyncMock()
    monkeypatch.setattr(database, "products_collection", mock_collection)
    monkeypatch.setattr(database, "user_history_collection", mock_collection)
    monkeypatch.setattr(database, "users_collection", mock_collection)
    monkeypatch.setattr(database, "spaces_collection", mock_collection)
    monkeypatch.setattr(database, "styles_collection", mock_collection)


    yield
