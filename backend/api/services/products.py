from backend.api.schemas.products import *
from backend.api.models.products import ProductDB
from backend.api.db.database import products_collection
from bson import ObjectId
import pandas as pd
from io import BytesIO
from pydantic import ValidationError
from backend.api.ml.categorization import categorize_product_by_description
from backend.api.ml.recomender import recommend_by_cosine_similarity
from datetime import datetime, timezone

async def list_products(skip: int = 0, limit: int = 10):
    products = await products_collection.find().skip(skip).limit(limit).to_list(length=limit)
    return [from_mongo(product, ProductRead) for product in products]

async def get_product(id: str):
    if not ObjectId.is_valid(id):
        return None
    product = await products_collection.find_one({"_id": ObjectId(id)})
    return from_mongo(product, ProductRead)
    

async def create_product(product_data: ProductCreate):
    category, spaces, styles = categorize_product_by_description(product_data.description)
    if not product_data.category:
        product_data.category = category
    if not product_data.spaces:
        product_data.spaces = spaces
    if not product_data.styles:
        product_data.styles = styles

    product_data_db = ProductDB(**product_data.model_dump())
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

async def delete_all_products():
    await products_collection.delete_many({})
    return True

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

async def import_products_from_excel(file_bytes: bytes) -> int:
    df = pd.read_excel(BytesIO(file_bytes))
    df = df.astype(object).where(pd.notnull(df), None)
    products = df.to_dict(orient="records")
    valid_products = []

    for product in products:
        try:
            validated = ProductCreate(**product)
            existing = await products_collection.count_documents({
                "purchase_link": str(validated.purchase_link)  # 🔁 convertir a string
            })
            if existing == 0:
                valid_products.append(validated.model_dump(mode="json"))  # 🔁 usar modo json (convierte automáticamente HttpUrl a string)
        except ValidationError as e:
            continue

    if valid_products:
        await products_collection.insert_many(valid_products)

    return len(valid_products)

async def get_product_recommendations(id: str, number: int = 5) -> List[ProductRead] | None:
    if not ObjectId.is_valid(id):
        return None

    product = await get_product(id)
    if not product:
        return None

    products = await list_products(limit=1000)
    recommendations = recommend_by_cosine_similarity(str(product.id), products, number)
    return recommendations
    

async def get_product_reviews(product_id: str) -> List[ProductReview] | None:
    product = await get_product(product_id)
    if not product:
        return None
    reviews = product.reviews or []
    reviews.sort(key=lambda r: r.get("timestamp") or "", reverse=True)
    return [ProductReview(**review) for review in reviews]

async def add_product_review(product_id: str, review: ProductReviewCreate) -> ProductReview | None:
    product = await get_product(product_id)
    if not product:
        return None

    new_review = review.dict()
    new_review["timestamp"] = datetime.now(timezone.utc)

    updated_reviews = product.reviews or []
    updated_reviews.append(new_review)

    review_count = len(updated_reviews)
    rating = round(sum(r["rating"] for r in updated_reviews) / review_count, 2)

    update_data = ProductUpdate(
        reviews=updated_reviews,
        review_count=review_count,
        rating=rating
    )

    await update_product(product_id, update_data)
    return ProductReview(**new_review)
