from backend.api.schemas.styles import *
from backend.api.models.styles import StyleDB
from backend.api.db.database import styles_collection
from bson import ObjectId

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


async def delete_style(id: str):
    if not ObjectId.is_valid(id):
        return None
    style = await get_style(id)
    if style:
        await styles_collection.delete_one({"_id": ObjectId(id)})
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