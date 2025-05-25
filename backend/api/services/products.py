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
from typing import List
from backend.api.services.categorization_service import load_embeddings

async def list_products(skip: int = 0, limit: int = 10):
    products = await products_collection.find().skip(skip).limit(limit).to_list(length=limit)
    return [from_mongo(product, ProductRead) for product in products]

async def get_product(id: str):
    if not ObjectId.is_valid(id):
        return None
    product = await products_collection.find_one({"_id": ObjectId(id)})
    return from_mongo(product, ProductRead)
    

async def create_product(product_data: ProductCreate, n_spaces: int = 3, n_styles: int = 3):
    category_embeddings, space_embeddings, style_embeddings, space_names, style_names = await load_embeddings()
    category, spaces, styles = categorize_product_by_description(product_data.description,
                                                                category_embeddings,
                                                                space_embeddings,
                                                                style_embeddings,
                                                                space_names,
                                                                style_names,
                                                                n_spaces=n_spaces,
                                                                n_styles=n_styles)
    product_data.category = category or product_data.category
    spaces = spaces or product_data.spaces or []
    styles = styles or product_data.styles or []
    product_data.spaces = spaces
    product_data.styles = styles

    product_data.rating = product_data.rating or 0.0
    product_data.review_count = product_data.review_count or 0
    product_data.reviews = product_data.reviews or []

    product_data_db = ProductDB(**product_data.model_dump())
    existing_products = await products_collection.count_documents({"purchase_link": product_data_db.purchase_link})
    if existing_products > 0:
        return None  
    product_insert_db = await products_collection.insert_one(product_data_db.to_dict())
    document = await products_collection.find_one({"_id": product_insert_db.inserted_id})
    return from_mongo(document, ProductRead)

async def create_products(products_data: List[ProductCreate], n_spaces: int = 3, n_styles: int = 3):
    category_embeddings, space_embeddings, style_embeddings, space_names, style_names = await load_embeddings()
    valid_products = []
    existing_products = []

    for product_data in products_data:           
        category, spaces, styles = categorize_product_by_description(
            product_data.description,
            category_embeddings,
            space_embeddings,
            style_embeddings,
            space_names,
            style_names,
            n_spaces=n_spaces,
            n_styles=n_styles
        )
        product_data.category = product_data.category or category
        product_data.spaces = product_data.spaces or spaces
        product_data.styles = product_data.styles or styles

        product_data.rating = product_data.rating or 0.0
        product_data.review_count = product_data.review_count or 0
        product_data.reviews = product_data.reviews or []

        product_db = ProductDB(**product_data.model_dump())

        existing_doc = await products_collection.find_one({"purchase_link": product_db.purchase_link})
        if existing_doc:
            existing_products.append(from_mongo(existing_doc, ProductRead))
        else:
            valid_products.append(product_db.to_dict())

    created_products = []
    if valid_products:
        result = await products_collection.insert_many(valid_products)
        inserted_docs = await products_collection.find(
            {"_id": {"$in": result.inserted_ids}}
        ).to_list(length=len(result.inserted_ids))
        created_products = [from_mongo(doc, ProductRead) for doc in inserted_docs]

    return {
        "created": created_products,
        "existing": existing_products
    }



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
