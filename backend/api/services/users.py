from backend.api.schemas.users import *
from backend.api.models.users import UserDB
from backend.api.db.database import users_collection
from bson import ObjectId
from backend.api.services.auth_service import get_password_hash
from backend.api.services  import products as products_service
from backend.api.services import user_history as user_history_service
from backend.api.schemas.user_history import UserHistoryCreate


async def list_users(skip: int = 0, limit: int = 10):
    users = await users_collection.find().skip(skip).limit(limit).to_list(length=limit)
    return [from_mongo(user, UserRead) for user in users]

async def get_user(id: str):
    if not ObjectId.is_valid(id):
        return None
    user = await users_collection.find_one({"_id": ObjectId(id)})
    return from_mongo(user, UserRead)
    

async def create_user(user_data: UserCreate):
    user_data.password = get_password_hash(user_data.password)
    user_data_db = UserDB(**user_data.model_dump())
    existing_users = await users_collection.count_documents({
        "$or": [
            {"username": user_data_db.username},
            {"email": user_data_db.email}
        ]
    })
    if existing_users > 0:
        return None  
    user_insert_db = await users_collection.insert_one(user_data_db.to_dict())
    document = await users_collection.find_one({"_id": user_insert_db.inserted_id})
    return from_mongo(document, UserRead)


async def delete_all_users():
    result = await users_collection.delete_many({})
    return result.deleted_count


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
        if updated_data.username or updated_data.email:
            existing_users = await users_collection.count_documents({
                "$or": [
                    {"username": updated_data.username},
                    {"email": updated_data.email}
                ]
            })
            if existing_users > 0:
                return None
        if updated_data.password:
            updated_data.password = get_password_hash(updated_data.password)
        await users_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_data.model_dump(exclude_unset=True)
})
        return await get_user(id)
    return None


async def get_cart_products(user_id: str):
    if not ObjectId.is_valid(user_id):
        return None
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return user.get("cart_products", [])
    return None

async def add_cart_product(user_id: str, product_id: str, quantity: int = 1):
    if not ObjectId.is_valid(user_id):
        return None

    product = await products_service.get_product(product_id)
    if not product:
        return False

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None

    cart = user.get("cart_products", [])
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            break
    else:
        cart.append({"product_id": product_id, "quantity": quantity})

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"cart_products": cart}}
    )

    await user_history_service.create_user_history(
        UserHistoryCreate(product_id=product_id, action="like"),
        user_id
    )

    return True



async def remove_cart_product(user_id: str, product_id: str):
    if not ObjectId.is_valid(user_id):
        return None

    result = await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"cart_products": {"product_id": product_id}}}
    )
    return result.modified_count > 0

async def update_product_quantity(user_id: str, product_id: str, new_quantity: int):
    if not ObjectId.is_valid(user_id):
        return None

    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return None

    updated = False
    cart = user.get("cart_products", [])
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] = int(new_quantity)
            updated = True
            break

    if not updated:
        return False

    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"cart_products": cart}}
    )
    return True

async def clear_cart(user_id: str):
    if not ObjectId.is_valid(user_id):
        return None
    await users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"cart_products": []}}
    )
    return True


