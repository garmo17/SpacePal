from backend.api.schemas.spaces import *
from backend.api.models.spaces import SpaceDB
from backend.api.db.database import spaces_collection, products_collection
from bson import ObjectId
from typing import List

async def list_spaces(skip: int = 0, limit: int = 10):
    spaces = await spaces_collection.find().skip(skip).limit(limit).to_list(length=limit)
    total = await spaces_collection.count_documents({})
    return [from_mongo(space, SpaceRead) for space in spaces], total

async def get_space(id: str):
    if not ObjectId.is_valid(id):
        return None
    space = await spaces_collection.find_one({"_id": ObjectId(id)})
    return from_mongo(space, SpaceRead)
    

async def create_space(space_data: SpaceCreate):
    space_data_db = SpaceDB(**space_data.model_dump())
    existing_spaces = await spaces_collection.count_documents({"name": space_data_db.name})
    if existing_spaces > 0:
        return None  
    space_insert_db = await spaces_collection.insert_one(space_data_db.to_dict())
    document = await spaces_collection.find_one({"_id": space_insert_db.inserted_id})
    return from_mongo(document, SpaceRead)

async def create_spaces(spaces_data: List[SpaceCreate]):
    spaces_db = [SpaceDB(**space_data.model_dump()) for space_data in spaces_data]
    space_names = [space.name for space in spaces_db]

    existing_docs = await spaces_collection.find({"name": {"$in": space_names}}).to_list(length=len(space_names))
    existing_names = [doc["name"] for doc in existing_docs]

    new_spaces = [space for space in spaces_db if space.name not in existing_names]

    if new_spaces:
        insert_result = await spaces_collection.insert_many([space.to_dict() for space in new_spaces])
        created_docs = await spaces_collection.find({"_id": {"$in": insert_result.inserted_ids}}).to_list(length=len(insert_result.inserted_ids))
        created_spaces = [from_mongo(doc, SpaceRead) for doc in created_docs]
    else:
        created_spaces = []

    existing_spaces = [from_mongo(doc, SpaceRead) for doc in existing_docs]

    return {
        "created": created_spaces,
        "existing": existing_spaces
    }



async def delete_space(id: str):
    if not ObjectId.is_valid(id):
        return None
    space = await get_space(id)
    if space:
        await spaces_collection.delete_one({"_id": ObjectId(id)})

        await products_collection.update_many(
            {},
            {"$pull": {"spaces": id}}
        )

        return space
    return None

async def update_space(id: str, updated_data: SpaceUpdate):
    if not ObjectId.is_valid(id):
        return None
    space = await get_space(id)
    if space:

        update_dict = updated_data.model_dump(exclude_unset=True)

        def convert_value(value):
            if isinstance(value, HttpUrl):
                return str(value)
            return value
        
        update_dict = {key: convert_value(value) for key, value in update_dict.items()}

        await spaces_collection.update_one({"_id": ObjectId(id)}, {"$set": update_dict})
        return await get_space(id)
    return None