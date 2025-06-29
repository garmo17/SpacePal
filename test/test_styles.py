import pytest
from unittest.mock import patch
from backend.api.schemas.styles import StyleRead
from fastapi.encoders import jsonable_encoder

# GET /styles/
@pytest.mark.asyncio
async def test_get_styles_success(async_client):
    fake_styles = [
        StyleRead(name="Modern", description="Minimalist and clean", image="http://example.com/modern.jpg", id="style1"),
        StyleRead(name="Boho", description="Colorful and cozy", image="http://example.com/boho.jpg", id="style2"),
    ]

    fake_total = len(fake_styles)

    with patch("backend.api.services.styles.list_styles", return_value=(fake_styles, fake_total)):
        response = await async_client.get("/api/v1/styles/")

    assert response.status_code == 200
    assert response.json() == jsonable_encoder(fake_styles)
    assert response.headers["Content-Range"] == f"0-{fake_total-1}/{fake_total}"

# GET /styles/ -> 404
@pytest.mark.asyncio
async def test_get_styles_empty(async_client):
    with patch("backend.api.services.styles.list_styles", return_value=([], 0)):
        response = await async_client.get("/api/v1/styles/")

    assert response.status_code == 404
    assert response.json()["detail"] == "No styles found"

# GET /styles/{id}
@pytest.mark.asyncio
async def test_get_style_by_id_success(async_client):
    fake_style = StyleRead(name="Scandi", description="Simple and warm", image="http://example.com/scandi.jpg", id="style3")

    with patch("backend.api.services.styles.get_style", return_value=fake_style):
        response = await async_client.get("/api/v1/styles/style3")

    assert response.status_code == 200
    assert response.json() == jsonable_encoder(fake_style)

# GET /styles/{id} -> 404
@pytest.mark.asyncio
async def test_get_style_not_found(async_client):
    with patch("backend.api.services.styles.get_style", return_value=None):
        response = await async_client.get("/api/v1/styles/invalid")

    assert response.status_code == 404
    assert response.json()["detail"] == "Style not found"

# POST /styles/
@pytest.mark.asyncio
async def test_create_style_success(async_client, override_is_admin):
    data = {
        "name": "Industrial",
        "description": "Metal and concrete",
        "image": "http://example.com/industrial.jpg"
    }
    created = StyleRead(**data, id="style_new")

    with patch("backend.api.services.styles.create_style", return_value=created):
        response = await async_client.post("/api/v1/styles/", json=data)

    assert response.status_code == 201
    assert response.json() == jsonable_encoder(created)

# POST /styles/ -> 409
@pytest.mark.asyncio
async def test_create_style_conflict(async_client, override_is_admin):
    data = {
        "name": "Modern",
        "description": "Duplicate",
        "image": "http://example.com/modern.jpg"
    }

    with patch("backend.api.services.styles.create_style", return_value=None):
        response = await async_client.post("/api/v1/styles/", json=data)

    assert response.status_code == 409
    assert response.json()["detail"] == "Style already exists"


# POST /styles/bulk
@pytest.mark.asyncio
async def test_create_styles_bulk_api_with_existing(async_client, override_is_admin):
    styles_data = [
        {
            "name": "Minimalista",
            "description": "Estilo sencillo y elegante.",
            "image": "http://example.com/minimalista.jpg"
        },
        {
            "name": "Industrial",
            "description": "Estilo urbano con metales y hormigón.",
            "image": "http://example.com/industrial.jpg"
        }
    ]

    created_style = StyleRead(
        name="Minimalista",
        description="Estilo sencillo y elegante.",
        image="http://example.com/minimalista.jpg",
        id="style_minimalista"
    )
    existing_style = StyleRead(
        name="Industrial",
        description="Estilo urbano con metales y hormigón.",
        image="http://example.com/industrial.jpg",
        id="style_industrial"
    )

    with patch("backend.api.services.styles.create_styles", return_value={
        "created": [created_style],
        "existing": [existing_style]
    }):
        response = await async_client.post("/api/v1/styles/bulk", json=styles_data)

    assert response.status_code == 201
    assert response.json() == {
        "created": [jsonable_encoder(created_style)],
        "existing": [jsonable_encoder(existing_style)]
    }

# PUT /styles/{id}
@pytest.mark.asyncio
async def test_update_style_success(async_client, override_is_admin):
    updated = StyleRead(name="Scandi", description="Warm neutral update", image="http://example.com/scandi-new.jpg", id="style3")

    with patch("backend.api.services.styles.update_style", return_value=updated):
        response = await async_client.put("/api/v1/styles/style3", json={"description": "Warm neutral update"})

    assert response.status_code == 200
    assert response.json() == jsonable_encoder(updated)

# PUT /styles/{id} -> 404
@pytest.mark.asyncio
async def test_update_style_not_found(async_client, override_is_admin):
    with patch("backend.api.services.styles.update_style", return_value=None):
        response = await async_client.put("/api/v1/styles/invalid", json={"name": "X"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Style not found"

# DELETE /styles/{id}
@pytest.mark.asyncio
async def test_delete_style_success(async_client, override_is_admin):
    with patch("backend.api.services.styles.delete_style", return_value=True):
        response = await async_client.delete("/api/v1/styles/style3")

    assert response.status_code == 200
    assert response.json() == {"message": "Style deleted successfully"}

# DELETE /styles/{id} -> 404
@pytest.mark.asyncio
async def test_delete_style_not_found(async_client, override_is_admin):
    with patch("backend.api.services.styles.delete_style", return_value=None):
        response = await async_client.delete("/api/v1/styles/invalid")

    assert response.status_code == 404
    assert response.json()["detail"] == "Style not found"
