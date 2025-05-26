import pytest
from unittest.mock import patch, AsyncMock
from bson import ObjectId
from backend.api.services.spaces import *
from backend.api.schemas.spaces import SpaceCreate, SpaceUpdate, SpaceRead
from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_list_spaces_returns_list():
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

    with patch("backend.api.db.database.spaces_collection.find", return_value=mock_find_chain):
        result = await list_spaces()

    assert isinstance(result, list)
    assert result[0].name == "Modern"





@pytest.mark.asyncio
async def test_get_space_success():
    space_id = ObjectId()
    mock_doc = {
        "_id": space_id, "name": "Boho", "description": "Colorful",
        "image": "http://example.com/boho.jpg"
    }

    with patch("backend.api.db.database.spaces_collection.find_one", new_callable=AsyncMock, return_value=mock_doc):
        result = await get_space(str(space_id))
        assert result.name == "Boho"


@pytest.mark.asyncio
async def test_get_space_invalid_id():
    result = await get_space("invalid")
    assert result is None


@pytest.mark.asyncio
async def test_create_space_conflict():
    data = SpaceCreate(name="Scandi", description="Light", image="http://example.com/scandi.jpg")
    with patch("backend.api.db.database.spaces_collection.count_documents", new=AsyncMock(return_value=1)):
        result = await create_space(data)
        assert result is None


@pytest.mark.asyncio
async def test_create_space_success():
    data = SpaceCreate(name="Industrial", description="Rough", image="http://example.com/ind.jpg")
    inserted_id = ObjectId()
    mock_doc = {
        "_id": inserted_id, "name": "Industrial", "description": "Rough",
        "image": "http://example.com/ind.jpg"
    }

    mock_insert_result = AsyncMock()
    mock_insert_result.inserted_id = inserted_id

    with patch("backend.api.db.database.spaces_collection.count_documents", new_callable=AsyncMock, return_value=0), \
         patch("backend.api.db.database.spaces_collection.insert_one", new_callable=AsyncMock, return_value=mock_insert_result), \
         patch("backend.api.db.database.spaces_collection.find_one", new_callable=AsyncMock, return_value=mock_doc):

        result = await create_space(data)

    assert result.name == "Industrial"


@pytest.mark.asyncio
async def test_create_spaces_bulk_success():
    # Datos de entrada simulados
    spaces_data = [
        SpaceCreate(
            name="Salón",
            description="Espacio para reuniones familiares con sofá y TV.",
            image="http://example.com/salon.jpg"
        ),
        SpaceCreate(
            name="Cocina",
            description="Espacio funcional con encimeras amplias.",
            image="http://example.com/cocina.jpg"
        )
    ]

    # Uno ya existe, otro será creado
    existing_doc = {
        "_id": ObjectId(),
        "name": "Salón",
        "description": "Espacio para reuniones familiares con sofá y TV.",
        "image": "http://example.com/salon.jpg"
    }

    created_doc = {
        "_id": ObjectId(),
        "name": "Cocina",
        "description": "Espacio funcional con encimeras amplias.",
        "image": "http://example.com/cocina.jpg"
    }


    with patch("backend.api.services.spaces.spaces_collection.count_documents", AsyncMock(return_value=1)), \
         patch("backend.api.services.spaces.spaces_collection.find") as mock_find, \
         patch("backend.api.services.spaces.spaces_collection.insert_many", AsyncMock(return_value=AsyncMock(inserted_ids=[created_doc["_id"]]))):
        
        mock_find.side_effect = [
                AsyncMock(to_list=AsyncMock(return_value=[existing_doc])),
                AsyncMock(to_list=AsyncMock(return_value=[created_doc]))
        ]

        result = await create_spaces(spaces_data)

        # Verifica que el resultado es un diccionario con claves 'created' y 'existing'
        assert isinstance(result, dict)
        assert "created" in result
        assert "existing" in result

        # Verifica que hay 1 creado y 1 existente
        assert len(result["created"]) == 1
        assert len(result["existing"]) == 1

        # Comprueba los datos creados
        created = result["created"][0]
        assert isinstance(created, SpaceRead)
        assert created.name == created_doc["name"]

        # Comprueba los datos existentes
        existing = result["existing"][0]
        assert isinstance(existing, SpaceRead)
        assert existing.name == existing_doc["name"]


@pytest.mark.asyncio
async def test_update_space_success():
    space_id = str(ObjectId())
    updated = SpaceUpdate(description="Updated")
    old = SpaceRead(id=space_id, name="Boho", description="Old", image="http://example.com/img.jpg")
    new = SpaceRead(id=space_id, name="Boho", description="Updated", image="http://example.com/img.jpg")

    with patch("backend.api.services.spaces.get_space", side_effect=[old, new]), \
         patch("backend.api.db.database.spaces_collection.update_one", new_callable=AsyncMock):

        result = await update_space(space_id, updated)

    assert result.description == "Updated"



@pytest.mark.asyncio
async def test_delete_space_success():
    space_id = str(ObjectId())
    fake_space = SpaceRead(id=space_id, name="Modern", description="Desc", image="http://example.com/image.jpg")

    with patch("backend.api.services.spaces.get_space", return_value=fake_space), \
         patch("backend.api.db.database.spaces_collection.delete_one", new_callable=AsyncMock):

        result = await delete_space(space_id)

    assert isinstance(result, SpaceRead)
    assert result.id == space_id




@pytest.mark.asyncio
async def test_delete_space_invalid_id():
    result = await delete_space("invalid")
    assert result is None