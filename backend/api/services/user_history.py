from backend.api.schemas.user_history import UserHistoryCreate, UserHistoryRead, from_mongo
from backend.api.models.user_history import UserHistoryDB
from backend.api.db.database import user_history_collection
from bson import ObjectId
from datetime import datetime, timezone
from typing import List


async def get_all_user_histories(skip: int = 0, limit: int = 10) -> List[UserHistoryRead]:
    cursor = user_history_collection.find().skip(skip).limit(limit)
    history_docs = await cursor.to_list(length=limit)
    total_count = await user_history_collection.count_documents({})
    return [from_mongo(doc, UserHistoryRead) for doc in history_docs], total_count


async def create_user_history(history_data: UserHistoryCreate, user_id: str) -> UserHistoryRead | None:
    entry = UserHistoryDB(
        user_id=user_id,
        product_id=history_data.product_id,
        action=history_data.action,
        timestamp=datetime.now(timezone.utc)
    )
    
    count = await user_history_collection.count_documents({"user_id": user_id})

    if count >= 50:
        oldest_entry = await user_history_collection.find_one({"user_id": user_id}, sort=[("timestamp", 1)])
        if oldest_entry:
            await user_history_collection.delete_one({"_id": oldest_entry["_id"]})

    await user_history_collection.insert_one(entry.to_dict())
    document = await user_history_collection.find_one({"_id": entry._id})
    return from_mongo(document, UserHistoryRead)

async def get_user_history(user_id: str, skip: int = 0, limit: int = 50) -> List[UserHistoryRead]:
    cursor = user_history_collection.find({"user_id": user_id}).sort("timestamp", -1).skip(skip).limit(limit)
    history_docs = await cursor.to_list(length=limit)
    return [from_mongo(doc, UserHistoryRead) for doc in history_docs]

async def delete_user_history(user_id: str) -> bool:
    result = await user_history_collection.delete_many({"user_id": user_id})
    return result.deleted_count > 0
