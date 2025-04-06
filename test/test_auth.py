# test/test_auth.py
import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from backend.api.main import app

@pytest.mark.asyncio
async def test_login_successful():
    fake_user = AsyncMock()
    fake_user.username = "testuser"
    fake_user.email = "testuser@example.com"
    fake_user.password = "$2b$12$gU9MZkTjBtGJqLhUNW98HehJG8svOpzMNa9O5lH2xOiFZ.GV/1aaW"  # hash de "testpass"

    with patch("backend.api.services.auth_service.get_user", return_value=fake_user):
        with patch("backend.api.services.auth_service.verify_password", return_value=True):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post(
                    "api/v1/auth/token",
                    data={"username": "testuser", "password": "testpass"},
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert data["token_type"] == "bearer"

