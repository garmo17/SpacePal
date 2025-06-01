from backend.api.schemas.styles import *
from backend.api.models.styles import StyleDB
from backend.api.db.database import styles_collection, products_collection
from bson import ObjectId
from typing import List

async def list_styles(skip: int = 0, limit: int = 10):
    styles = await styles_collection.find().skip(skip).limit(limit).to_list(length=limit)
    return [from_mongo(style, StyleRead) for style in styles]

async def get_style(id: str):
    if not ObjectId.is_valid(id):
        return None
    style = await styles_collection.find_one({"_id": ObjectId(id)})
    return from_mongo(style, StyleRead)
    

async def create_style(style_data: StyleCreate):
    style_data_db = StyleDB(**style_data.model_dump())
    existing_styles = await styles_collection.count_documents({"name": style_data_db.name})
    if existing_styles > 0:
        return None  
    style_insert_db = await styles_collection.insert_one(style_data_db.to_dict())
    document = await styles_collection.find_one({"_id": style_insert_db.inserted_id})
    return from_mongo(document, StyleRead)

async def create_styles(styles_data: List[StyleCreate]):
    styles_db = [StyleDB(**style_data.model_dump()) for style_data in styles_data]
    style_names = [style.name for style in styles_db]

    existing_docs = await styles_collection.find({"name": {"$in": style_names}}).to_list(length=len(style_names))
    existing_names = [doc["name"] for doc in existing_docs]

    new_styles = [style for style in styles_db if style.name not in existing_names]

    if new_styles:
        insert_result = await styles_collection.insert_many([style.to_dict() for style in new_styles])
        created_docs = await styles_collection.find({"_id": {"$in": insert_result.inserted_ids}}).to_list(length=len(insert_result.inserted_ids))
        created_styles = [from_mongo(doc, StyleRead) for doc in created_docs]
    else:
        created_styles = []

    existing_styles = [from_mongo(doc, StyleRead) for doc in existing_docs]

    return {
        "created": created_styles,
        "existing": existing_styles
    }


async def delete_style(id: str):
    if not ObjectId.is_valid(id):
        return None
    style = await get_style(id)
    if style:
        await styles_collection.delete_one({"_id": ObjectId(id)})

        await products_collection.update_many(
            {},
            {"$pull": {"styles": id}}
        )

        return style
    return None

async def update_style(id: str, updated_data: StyleUpdate):
    if not ObjectId.is_valid(id):
        return None
    style = await get_style(id)
    if style:

        updated_dict = updated_data.model_dump(exclude_unset=True)

        def convert_value(value):
            if isinstance(value, HttpUrl):
                return str(value)
            return value

        updated_dict = {key: convert_value(value) for key, value in updated_dict.items()}

        await styles_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_dict})

        return await get_style(id)
    return None