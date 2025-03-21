from schemas.spaces import *
from models.spaces import SpaceDB
from db.database import spaces_collection
from bson import ObjectId

async def list_spaces(skip: int = 0, limit: int = 10):
    spaces = await spaces_collection.find().skip(skip).limit(limit).to_list(length=limit)
    return [from_mongo(space, SpaceRead) for space in spaces]

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


async def delete_space(id: str):
    if not ObjectId.is_valid(id):
        return None
    space = await get_space(id)
    if space:
        await spaces_collection.delete_one({"_id": ObjectId(id)})
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