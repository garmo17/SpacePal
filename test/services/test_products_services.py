import pytest
from unittest.mock import patch, AsyncMock
from bson import ObjectId
from backend.api.schemas.products import ProductCreate, ProductUpdate, ProductRead
from backend.api.services.products import (
    list_products, get_product, create_product,
    delete_product, update_product, delete_all_products
)

from unittest.mock import MagicMock

@pytest.mark.asyncio
async def test_list_products_returns_list():
    mock_docs = [
        {
            "_id": ObjectId(),
            "name": "Lamp",
            "description": "LED",
            "price": 20.0,
            "purchase_link": "http://example.com/lamp",
            "image_url": "http://example.com/img.jpg",
            "category": "lighting",
            "spaces": ["living room"],
            "styles": ["modern"],
            "rating": 4.5,
            "review_count": 10,
            "reviews": []
        },
    ]

    mock_to_list = AsyncMock(return_value=mock_docs)
    mock_limit = MagicMock()
    mock_limit.to_list = mock_to_list
    mock_skip = MagicMock()
    mock_skip.limit.return_value = mock_limit

    mock_find_chain = MagicMock()
    mock_find_chain.skip.return_value = mock_skip

    with patch("backend.api.db.database.products_collection.find", return_value=mock_find_chain):
        result = await list_products()

    assert isinstance(result, list)
    assert result[0].name == "Lamp"





@pytest.mark.asyncio
async def test_get_product_success():
    product_id = ObjectId()
    mock_doc = {
        "_id": product_id, "name": "Chair", "description": "Comfy", "price": 50.0,
        "purchase_link": "http://example.com/chair", "image_url": "http://example.com/chair.jpg", "category": "furniture", 
        "spaces": ["office"], "styles": ["modern"], "rating": 4.0, "review_count": 5, "reviews": []
    }

    with patch("backend.api.db.database.products_collection.find_one", AsyncMock(return_value=mock_doc)):
        result = await get_product(str(product_id))
        assert result.name == "Chair"
        assert result.id == str(product_id)


@pytest.mark.asyncio
async def test_get_product_invalid_id():
    result = await get_product("invalid_id")
    assert result is None


@pytest.mark.asyncio
async def test_create_product_conflict():
    data = ProductCreate(
        name="Lamp", description="Dup", price=10.0,
        purchase_link="http://example.com/lamp", image_url="http://example.com/lamp.jpg", category="lighting",
        spaces=["living room"], styles=["modern"], rating=4.5, review_count=10, reviews=[]
    )

    mocked_embeddings = (
        [[0.1]*768],
        [[0.1]*768, [0.1]*768, [0.1]*768],
        [[0.1]*768, [0.1]*768, [0.1]*768],
        ["living room", "office", "dining room"],
        ["rustic", "modern", "minimalist"]
    )


    with patch("backend.api.db.database.products_collection.count_documents", AsyncMock(return_value=1)), \
         patch("backend.api.services.products.load_embeddings", AsyncMock(return_value = mocked_embeddings)):
        result = await create_product(data)
        assert result is None


@pytest.mark.asyncio
async def test_create_product_success():
    data = ProductCreate(
        name="Table", description="Wood", price=80.0,
        purchase_link="http://example.com/table", image_url="http://example.com/table.jpg", category="furniture",
        spaces=["dining room"], styles=["rustic"], rating=4.2, review_count=8, reviews=[]
    )
    inserted_id = ObjectId()
    mock_doc = {
        "_id": inserted_id, "name": "Table", "description": "Wood", "price": 80.0,
        "purchase_link": "http://example.com/table", "image_url": "http://example.com/table.jpg", "category": "furniture",
        "spaces": ["dining room"], "styles": ["rustic"], "rating": 4.2, "review_count": 8, "reviews": []
    }

    mocked_embeddings = (
        [[0.1]*768],
        [[0.1]*768, [0.1]*768, [0.1]*768],
        [[0.1]*768, [0.1]*768, [0.1]*768],
        ["living room", "office", "dining room"],
        ["rustic", "modern", "minimalist"]
    )

    with patch("backend.api.db.database.products_collection.count_documents", AsyncMock(return_value=0)), \
         patch("backend.api.db.database.products_collection.insert_one", AsyncMock(return_value=AsyncMock(inserted_id=inserted_id))), \
         patch("backend.api.db.database.products_collection.find_one", AsyncMock(return_value=mock_doc)), \
         patch("backend.api.services.products.load_embeddings", AsyncMock(return_value = mocked_embeddings)):

        result = await create_product(data)
        assert result.name == "Table"
        assert result.id == str(inserted_id)


@pytest.mark.asyncio
async def test_create_product_no_category_space_style():
    data = ProductCreate(
        name="Desk", description="Office desk", price=120.0,
        purchase_link="http://example.com/desk", image_url="http://example.com/desk.jpg"
    )
    inserted_id = ObjectId()
    mock_doc = {
        "_id": inserted_id, "name": "Desk", "description": "Office desk", "price": 120.0,
        "purchase_link": "http://example.com/desk", "image_url": "http://example.com/desk.jpg", "category": "desks and desk chairs",
        "spaces": ["office"], "styles": ["modern"],
        "rating": 0.0, "review_count": 0, "reviews": []
    }

    mocked_embeddings = (
        [[0.1]*768],
        [[0.1]*768, [0.1]*768, [0.1]*768],
        [[0.1]*768, [0.1]*768, [0.1]*768],
        ["living room", "office", "dining room"],
        ["rustic", "modern", "minimalist"]
    )

    with patch("backend.api.db.database.products_collection.count_documents", AsyncMock(return_value=0)), \
        patch("backend.api.db.database.products_collection.insert_one", AsyncMock(return_value=AsyncMock(inserted_id=inserted_id))), \
        patch("backend.api.db.database.products_collection.find_one", AsyncMock(return_value=mock_doc)), \
        patch("backend.api.services.products.categorize_product_by_description", return_value=("desks and desk chairs", ["office"], ["modern"])), \
        patch("backend.api.services.products.load_embeddings", AsyncMock(return_value=mocked_embeddings)):

        result = await create_product(data)
        assert result.name == "Desk"
        assert result.category == "desks and desk chairs"
        assert result.spaces == ["office"]
        assert result.styles == ["modern"]


@pytest.mark.asyncio
async def test_delete_product_success():
    product_id = str(ObjectId())
    mock_product = ProductRead(
        id=product_id, name="Shelf", description="Wall-mounted", price=45.0,
        purchase_link="http://example.com/shelf", image_url="http://example.com/shelf.jpg", category="storage",
        spaces=["living room"], styles=["modern"], rating=4.0, review_count=3, reviews=[]
    )

    with patch("backend.api.services.products.get_product", AsyncMock(return_value=mock_product)), \
         patch("backend.api.db.database.products_collection.delete_one", AsyncMock()):
        result = await delete_product(product_id)
        assert result is mock_product


@pytest.mark.asyncio
async def test_delete_product_invalid_id():
    result = await delete_product("invalid_id")
    assert result is None

@pytest.mark.asyncio
async def test_delete_all_products_success():
    with patch("backend.api.db.database.products_collection.delete_many", AsyncMock()):
        result = await delete_all_products()
        assert result is True


@pytest.mark.asyncio
async def test_update_product_success():
    product_id = str(ObjectId())
    updated = ProductUpdate(description="Updated")
    updated_doc = {
        "_id": ObjectId(product_id), "name": "Lamp", "description": "Updated", "price": 29.99,
        "purchase_link": "http://example.com/lamp", "image_url": "http://example.com/lamp.jpg", "category": "lighting", "spaces": ["living room"], "styles": ["modern"], "rating": 4.5, "review_count": 10, "reviews": []
    }

    with patch("backend.api.services.products.get_product", side_effect=[
        ProductRead(id=product_id, name="Lamp", description="Old", price=29.99,
                    purchase_link="http://example.com/lamp", image_url="http://example.com/lamp.jpg", category="lighting", spaces=["living room"], styles=["modern"], rating=4.5, review_count=10, reviews=[]),
        ProductRead(**updated_doc, id=product_id)
    ]), patch("backend.api.db.database.products_collection.update_one", AsyncMock()):
        result = await update_product(product_id, updated)
        assert result.description == "Updated"

