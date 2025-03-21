from schemas.users import *
from models.users import UserDB
from db.database import users_collection
from bson import ObjectId

async def list_users(skip: int = 0, limit: int = 10):
    users = await users_collection.find().skip(skip).limit(limit).to_list(length=limit)
    return [from_mongo(user, UserRead) for user in users]

async def get_user(id: str):
    if not ObjectId.is_valid(id):
        return None
    user = await users_collection.find_one({"_id": ObjectId(id)})
    return from_mongo(user, UserRead)
    

async def create_user(user_data: UserCreate):
    user_data_db = UserDB(**user_data.model_dump())
    existing_users = await users_collection.count_documents({"email": user_data_db.email})
    if existing_users > 0:
        return None  
    user_insert_db = await users_collection.insert_one(user_data_db.to_dict())
    document = await users_collection.find_one({"_id": user_insert_db.inserted_id})
    return from_mongo(document, UserRead)


async def delete_user(id: str):
    if not ObjectId.is_valid(id):
        return None
    user = await get_user(id)
    if user:
        await users_collection.delete_one({"_id": ObjectId(id)})
        return user
    return None

async def update_user(id: str, updated_data: UserUpdate):
    if not ObjectId.is_valid(id):
        return None
    user = await get_user(id)
    if user:
        await users_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_data.model_dump(exclude_unset=True)
})
        return await get_user(id)
    return None


