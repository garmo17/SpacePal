import pytest
from unittest.mock import patch
from backend.api.schemas.products import ProductRead
from fastapi.encoders import jsonable_encoder

# GET /products/
@pytest.mark.asyncio
async def test_get_products_success(async_client):
    fake_products = [
        ProductRead(
            name="Lamp", description="LED Desk Lamp", price=29.99,
            purchase_link="http://example.com/lamp", image_url="http://example.com/lamp.jpg",
            category="lighting", id="prod1", spaces=["office"], styles=["modern"], rating=4.5, review_count=10, reviews=[]
        ),
        ProductRead(
            name="Chair", description="Office Chair", price=89.99,
            purchase_link="http://example.com/chair", image_url="http://example.com/chair.jpg",
            category="furniture", id="prod2", spaces=["office"], styles=["ergonomic"], rating=4.0, review_count=5, reviews=[]
        )
    ]

    with patch("backend.api.services.products.list_products", return_value=fake_products):
        response = await async_client.get("/api/v1/products/")

    assert response.status_code == 200
    assert response.json() == jsonable_encoder(fake_products)

# POST /products/ (success)
@pytest.mark.asyncio
async def test_create_product_success(async_client, override_is_admin):
    new_product = {
        "name": "Sofa",
        "description": "Comfortable sofa",
        "price": 399.99,
        "purchase_link": "http://example.com/sofa",
        "image_url": "http://example.com/sofa.jpg",
        "category": "furniture",
        "spaces": ["living room"],
        "styles": ["modern"],
        "rating": 4.8,
        "review_count": 20,
        "reviews": []
    }

    expected_response = ProductRead(**new_product, id="new123")

    with patch("backend.api.services.products.create_product", return_value=expected_response):
        response = await async_client.post("/api/v1/products/", json=new_product)

    assert response.status_code == 201
    assert response.json() == jsonable_encoder(expected_response)

# POST /products/ (conflict)
@pytest.mark.asyncio
async def test_create_product_conflict(async_client, override_is_admin):
    conflict_data = {
        "name": "Lamp",
        "description": "Duplicate lamp",
        "price": 29.99,
        "purchase_link": "http://example.com/lamp",
        "image_url": "http://example.com/lamp.jpg",
        "category": "lighting",
        "spaces": ["office"],
        "styles": ["modern"],
        "rating": 4.5,
        "review_count": 10,
        "reviews": []
    }

    with patch("backend.api.services.products.create_product", return_value=None):
        response = await async_client.post("/api/v1/products/", json=conflict_data)

    assert response.status_code == 409
    assert response.json()["detail"] == "Product already exists"

# POST /products/ (without category)
@pytest.mark.asyncio
async def test_create_product_without_category(async_client, override_is_admin):
    new_product = {
        "name": "Bookshelf",
        "description": "Wooden bookshelf",
        "price": 199.99,
        "purchase_link": "http://example.com/bookshelf",
        "image_url": "http://example.com/bookshelf.jpg"
    }



    expected_response = ProductRead(**new_product, id="new456", category="storage", spaces=["living room"], styles=["rustic"], rating=4.2, review_count=15, reviews=[])

    with patch("backend.api.services.products.create_product", return_value=expected_response):
        response = await async_client.post("/api/v1/products/", json=new_product)

    assert response.status_code == 201
    assert response.json() == jsonable_encoder(expected_response)

# GET /products/{id} (success)
@pytest.mark.asyncio
async def test_get_product_by_id_success(async_client):
    product = ProductRead(
        name="Shelf", description="Wall-mounted shelf", price=49.99,
        purchase_link="http://example.com/shelf", image_url="http://example.com/shelf.jpg",
        category="storage", id="prod123", spaces=["living room"], styles=["modern"], rating=4.0, review_count=3, reviews=[]
    )

    with patch("backend.api.services.products.get_product", return_value=product):
        response = await async_client.get("/api/v1/products/prod123")

    assert response.status_code == 200
    assert response.json() == jsonable_encoder(product)

# GET /products/{id} (not found)
@pytest.mark.asyncio
async def test_get_product_by_id_not_found(async_client):
    with patch("backend.api.services.products.get_product", return_value=None):
        response = await async_client.get("/api/v1/products/nonexistent")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

# PUT /products/{id} (success)
@pytest.mark.asyncio
async def test_update_product_success(async_client, override_is_admin):
    updated_product = ProductRead(
        name="Updated Lamp", description="Updated Desc", price=39.99,
        purchase_link="http://example.com/lamp-updated", image_url="http://example.com/lamp-updated.jpg",
        category="lighting", id="prod1", spaces=["office"], styles=["modern"], rating=4.5, review_count=10, reviews=[]
    )

    with patch("backend.api.services.products.update_product", return_value=updated_product):
        response = await async_client.put("/api/v1/products/prod1", json={"name": "Updated Lamp"})

    assert response.status_code == 200
    assert response.json() == jsonable_encoder(updated_product)

# PUT /products/{id} (not found)
@pytest.mark.asyncio
async def test_update_product_not_found(async_client, override_is_admin):
    with patch("backend.api.services.products.update_product", return_value=None):
        response = await async_client.put("/api/v1/products/invalid", json={"name": "Not Found"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

# DELETE /products/{id} (success)
@pytest.mark.asyncio
async def test_delete_product_success(async_client, override_is_admin):
    with patch("backend.api.services.products.delete_product", return_value=True):
        response = await async_client.delete("/api/v1/products/prod1")

    assert response.status_code == 200
    assert response.json() == {"message": "Product deleted successfully"}

# DELETE /products/{id} (not found)
@pytest.mark.asyncio
async def test_delete_product_not_found(async_client, override_is_admin):
    with patch("backend.api.services.products.delete_product", return_value=None):
        response = await async_client.delete("/api/v1/products/unknown")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

# DELETE /products/ (success)
@pytest.mark.asyncio
async def test_delete_all_products_success(async_client, override_is_admin):
    with patch("backend.api.services.products.delete_all_products", return_value=True):
        response = await async_client.delete("/api/v1/products/")

    assert response.status_code == 200
    assert response.json() == {"message": "All products deleted successfully"}
