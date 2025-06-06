from backend.api.schemas.products import *
from backend.api.models.products import ProductDB
from backend.api.db.database import products_collection, users_collection
from bson import ObjectId
import pandas as pd
from io import BytesIO
from pydantic import ValidationError
from backend.api.ml.categorization import categorize_product_by_description, category_labels
from backend.api.ml.recomender import recommend_by_cosine_similarity
from datetime import datetime, timezone
from typing import List
from backend.api.services.categorization_service import load_embeddings
import ast
from backend.api.db.database import spaces_collection, styles_collection

async def list_products(skip: int = 0, limit: int = 10):
    products = await products_collection.find().skip(skip).limit(limit).to_list(length=limit)
    total = await products_collection.count_documents({})
    return [from_mongo(product, ProductRead) for product in products], total

async def get_product(id: str):
    if not ObjectId.is_valid(id):
        return None
    product = await products_collection.find_one({"_id": ObjectId(id)})
    return from_mongo(product, ProductRead)


async def create_product(product_data: ProductCreate, n_spaces: int = 3, n_styles: int = 3):
    if product_data.category and product_data.category not in category_labels:
        return {"error": f"Categoría '{product_data.category}' no es válida. Debe ser una de: {category_labels}"}
    
    category_embeddings, space_embeddings, style_embeddings, space_names, style_names = await load_embeddings()
    category, spaces, styles = await categorize_product_by_description(
        product_data.description,
        category_embeddings,
        space_embeddings,
        style_embeddings,
        space_names,
        style_names,
        n_spaces=n_spaces,
        n_styles=n_styles
    )

    product_data.category = category or product_data.category

    if product_data.spaces:
        product_data.spaces = await validate_and_filter_existing_ids(product_data.spaces, spaces_collection)
    else:
        product_data.spaces = spaces or []

    if product_data.styles:
        product_data.styles = await validate_and_filter_existing_ids(product_data.styles, styles_collection)
    else:
        product_data.styles = styles or []

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
    skipped_count = 0

    for product_data in products_data:
        if product_data.category and product_data.category not in category_labels:
            skipped_count += 1
            print(f"Producto '{product_data.name}' tiene categoría inválida '{product_data.category}'. Saltando...")
            continue

        category, spaces, styles = await categorize_product_by_description(
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

        if product_data.spaces:
            product_data.spaces = await validate_and_filter_existing_ids(product_data.spaces, spaces_collection)
        else:
            product_data.spaces = spaces or []

        if product_data.styles:
            product_data.styles = await validate_and_filter_existing_ids(product_data.styles, styles_collection)
        else:
            product_data.styles = styles or []

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
        inserted_docs = await products_collection.find({"_id": {"$in": result.inserted_ids}}).to_list(length=len(result.inserted_ids))
        created_products = [from_mongo(doc, ProductRead) for doc in inserted_docs]

    return {
        "created": created_products,
        "existing": existing_products,
        "skipped": skipped_count,
    }



async def delete_product(id: str):
    if not ObjectId.is_valid(id):
        return None

    product = await get_product(id)
    if product:
        await products_collection.delete_one({"_id": ObjectId(id)})

        await users_collection.update_many(
            {},
            {"$pull": {"liked_products": id}}
        )

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

        if "category" in update_dict and update_dict["category"] not in category_labels:
            return {"error": f"Categoría '{update_dict['category']}' no es válida. Debe ser una de: {category_labels}"}

        if "spaces" in update_dict:
            update_dict["spaces"] = await validate_and_filter_existing_ids(update_dict["spaces"], spaces_collection)
        if "styles" in update_dict:
            update_dict["styles"] = await validate_and_filter_existing_ids(update_dict["styles"], styles_collection)

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


async def import_products_from_excel(file_bytes: bytes) -> dict:
    df = pd.read_excel(BytesIO(file_bytes))
    df = df.astype(object).where(pd.notnull(df), None)
    products = df.to_dict(orient="records")
    valid_products = []

    total_rows = len(products)
    skipped_count = 0

    for product in products:
        for key in ["spaces", "styles", "reviews"]:
            if isinstance(product.get(key), str):
                try:
                    product[key] = ast.literal_eval(product[key])
                except (ValueError, SyntaxError):
                    product[key] = []  
        try:
            validated = ProductCreate(**product)
            existing = await products_collection.count_documents({
                "purchase_link": str(validated.purchase_link)
            })
            if existing == 0:
                valid_products.append(validated.model_dump(mode="json"))
            else:
                skipped_count += 1
                print(f"Product {product.get('name', 'unknown')} already exists, skipping.")
        except ValidationError as e:
            skipped_count += 1
            print(f"Validation error for product {product.get('name', 'unknown')}: {e}")

    if valid_products:
        await products_collection.insert_many(valid_products)

    return {
        "inserted": len(valid_products),
        "skipped": skipped_count,
        "total": total_rows
    }

async def get_product_recommendations(id: str, number: int = 5) -> List[ProductRead] | None:
    if not ObjectId.is_valid(id):
        return None

    product = await get_product(id)
    if not product:
        return None

    products, _ = await list_products(limit=1000)
    recommendations = await recommend_by_cosine_similarity(str(product.id), products, number)
    return recommendations
    

async def get_product_reviews(product_id: str) -> List[ProductReview] | None:
    product = await get_product(product_id)
    if not product:
        return None
    reviews = product.reviews or []
    reviews.sort(key=lambda r: r.get("timestamp") or "", reverse=True)
    return [ProductReview(**review) for review in reviews]


async def add_product_review(product_id: str, review: ProductReviewCreate, user_id: str, username: str) -> ProductReview | None:
    product = await get_product(product_id)
    if not product:
        return None

    new_review = ProductReview(
        id=str(uuid4()),
        user_id=user_id,
        username=username,
        rating=review.rating,
        comment=review.comment,
        timestamp=datetime.now(timezone.utc)
    )

    updated_reviews = product.reviews or []
    updated_reviews.append(new_review)

    review_count = len(updated_reviews)
    rating = round(sum(r.rating if isinstance(r, ProductReview) else r["rating"] for r in updated_reviews) / review_count, 2)

    update_data = ProductUpdate(
        reviews=updated_reviews,
        review_count=review_count,
        rating=rating
    )

    await update_product(product_id, update_data)
    return new_review


async def delete_product_review(product_id: str, review_id: str, user_id: str) -> bool:
    product = await get_product(product_id)
    if not product:
        return False

    updated_reviews = [
        r for r in product.reviews
        if str(r.get("id") if isinstance(r, dict) else r.id) != review_id
    ]

    if len(updated_reviews) == len(product.reviews):
        return False

    review_count = len(updated_reviews)
    rating = round(
        sum(r["rating"] if isinstance(r, dict) else r.rating for r in updated_reviews) / review_count, 2
    ) if review_count > 0 else 0.0

    update_data = ProductUpdate(
        reviews=updated_reviews,
        review_count=review_count,
        rating=rating
    )

    await update_product(product_id, update_data)
    return True


async def get_products_by_space_and_style(space: str, style: str, categories: Optional[List[str]] = None, limit: int = 1000):
    query = {
        "spaces": space,
        "styles": style
    }
    if categories:
        query["category"] = {"$in": categories}

    products = await products_collection.find(query).to_list(length=limit)
    return products



async def validate_and_filter_existing_ids(ids: List[str], collection) -> List[str]:
    valid_ids = []
    for _id in ids:
        if ObjectId.is_valid(_id):
            obj_id = ObjectId(_id)
            exists = await collection.find_one({"_id": obj_id})
            if exists:
                valid_ids.append(str(obj_id))
    return valid_ids


