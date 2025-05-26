import pytest
from unittest.mock import patch, AsyncMock
from bson import ObjectId
from backend.api.services.styles import *
from backend.api.schemas.styles import StyleCreate, StyleUpdate, StyleRead
from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_list_styles_returns_list():
    mock_docs = [
        {
            "_id": ObjectId(), "name": "Modern", "description": "Clean",
            "image": "http://example.com/modern.jpg"
        }
    ]

    mock_to_list = AsyncMock(return_value=mock_docs)
    mock_limit = MagicMock()
    mock_limit.to_list = mock_to_list
    mock_skip = MagicMock()
    mock_skip.limit.return_value = mock_limit

    mock_find_chain = MagicMock()
    mock_find_chain.skip.return_value = mock_skip

    with patch("backend.api.db.database.styles_collection.find", return_value=mock_find_chain):
        result = await list_styles()

    assert isinstance(result, list)
    assert result[0].name == "Modern"





@pytest.mark.asyncio
async def test_get_style_success():
    style_id = ObjectId()
    mock_doc = {
        "_id": style_id, "name": "Boho", "description": "Colorful",
        "image": "http://example.com/boho.jpg"
    }

    with patch("backend.api.db.database.styles_collection.find_one", new_callable=AsyncMock, return_value=mock_doc):
        result = await get_style(str(style_id))
        assert result.name == "Boho"


@pytest.mark.asyncio
async def test_get_style_invalid_id():
    result = await get_style("invalid")
    assert result is None


@pytest.mark.asyncio
async def test_create_style_conflict():
    data = StyleCreate(name="Scandi", description="Light", image="http://example.com/scandi.jpg")
    with patch("backend.api.db.database.styles_collection.count_documents", new=AsyncMock(return_value=1)):
        result = await create_style(data)
        assert result is None


@pytest.mark.asyncio
async def test_create_style_success():
    data = StyleCreate(name="Industrial", description="Rough", image="http://example.com/ind.jpg")
    inserted_id = ObjectId()
    mock_doc = {
        "_id": inserted_id, "name": "Industrial", "description": "Rough",
        "image": "http://example.com/ind.jpg"
    }

    mock_insert_result = AsyncMock()
    mock_insert_result.inserted_id = inserted_id

    with patch("backend.api.db.database.styles_collection.count_documents", new_callable=AsyncMock, return_value=0), \
         patch("backend.api.db.database.styles_collection.insert_one", new_callable=AsyncMock, return_value=mock_insert_result), \
         patch("backend.api.db.database.styles_collection.find_one", new_callable=AsyncMock, return_value=mock_doc):

        result = await create_style(data)

    assert result.name == "Industrial"


@pytest.mark.asyncio
async def test_create_styles_bulk_success():
    styles_data = [
        StyleCreate(
            name="Minimalista",
            description="Estilo sencillo y elegante.",
            image="http://example.com/minimalista.jpg"
        ),
        StyleCreate(
            name="Industrial",
            description="Estilo urbano con metales y hormigón.",
            image="http://example.com/industrial.jpg"
        )
    ]

    created_doc = {
        "_id": ObjectId(),
        "name": "Minimalista",
        "description": "Estilo sencillo y elegante.",
        "image": "http://example.com/minimalista.jpg"
    }
    existing_doc = {
        "_id": ObjectId(),
        "name": "Industrial",
        "description": "Estilo urbano con metales y hormigón.",
        "image": "http://example.com/industrial.jpg"
    }

    with patch("backend.api.services.styles.styles_collection.find") as mock_find, \
    patch("backend.api.services.styles.styles_collection.insert_many", AsyncMock(return_value=AsyncMock(inserted_ids=[created_doc["_id"]]))):
        
        mock_find.side_effect = [
            AsyncMock(to_list=AsyncMock(return_value=[existing_doc])),
            AsyncMock(to_list=AsyncMock(return_value=[created_doc]))
        ]
        result = await create_styles(styles_data)

        assert isinstance(result, dict)
        assert "created" in result
        assert "existing" in result

        created = result["created"]
        existing = result["existing"]
        assert len(created) == 1
        assert created[0].name == "Minimalista"
        assert len(existing) == 1
        assert existing[0].name == "Industrial"

@pytest.mark.asyncio
async def test_update_style_success():
    style_id = str(ObjectId())
    updated = StyleUpdate(description="Updated")
    old = StyleRead(id=style_id, name="Boho", description="Old", image="http://example.com/img.jpg")
    new = StyleRead(id=style_id, name="Boho", description="Updated", image="http://example.com/img.jpg")

    with patch("backend.api.services.styles.get_style", side_effect=[old, new]), \
         patch("backend.api.db.database.styles_collection.update_one", new_callable=AsyncMock):

        result = await update_style(style_id, updated)

    assert result.description == "Updated"



@pytest.mark.asyncio
async def test_delete_style_success():
    style_id = str(ObjectId())
    fake_style = StyleRead(id=style_id, name="Modern", description="Desc", image="http://example.com/image.jpg")

    with patch("backend.api.services.styles.get_style", return_value=fake_style), \
         patch("backend.api.db.database.styles_collection.delete_one", new_callable=AsyncMock):

        result = await delete_style(style_id)

    assert isinstance(result, StyleRead)
    assert result.id == style_id




@pytest.mark.asyncio
async def test_delete_style_invalid_id():
    result = await delete_style("invalid")
    assert result is None
