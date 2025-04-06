from backend.api.schemas.products import *
from backend.api.models.products import ProductDB
from backend.api.db.database import products_collection
from bson import ObjectId

async def list_products(skip: int = 0, limit: int = 10):
    products = await products_collection.find().skip(skip).limit(limit).to_list(length=limit)
    return [from_mongo(product, ProductRead) for product in products]

async def get_product(id: str):
    if not ObjectId.is_valid(id):
        return None
    product = await products_collection.find_one({"_id": ObjectId(id)})
    return from_mongo(product, ProductRead)
    

async def create_product(product_data: ProductCreate):
    product_data_db = ProductDB(**product_data.model_dump())
    print(product_data_db.purchase_link.__class__)
    existing_products = await products_collection.count_documents({"purchase_link": product_data_db.purchase_link})
    if existing_products > 0:
        return None  
    product_insert_db = await products_collection.insert_one(product_data_db.to_dict())
    document = await products_collection.find_one({"_id": product_insert_db.inserted_id})
    return from_mongo(document, ProductRead)


async def delete_product(id: str):
    if not ObjectId.is_valid(id):
        return None
    product = await get_product(id)
    if product:
        await products_collection.delete_one({"_id": ObjectId(id)})
        return product
    return None

async def update_product(id: str, updated_data: ProductUpdate):
    if not ObjectId.is_valid(id):
        return None
    product = await get_product(id)
    if product:
        
        update_dict = updated_data.model_dump(exclude_unset=True)

        def convert_value(value):
            if isinstance(value, HttpUrl):
                return str(value)
            return value

        update_dict = {key: convert_value(value) for key, value in update_dict.items()}
        
        await products_collection.update_one(
            {"_id": ObjectId(id)}, 
            {"$set": update_dict}
            )
        return await get_product(id)
    return None
