
from typing import Optional, List
from fastapi import HTTPException
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from backend.api.models.users import UserDB
from backend.api.schemas.products import ProductRead
from backend.api.services import user_history as user_history_service
from backend.api.services import products as products_service
from backend.api.ml.recomender import vectorize_products
from backend.api.db.database import spaces_collection, styles_collection


async def get_personalized(space: str, style: str, user: Optional[UserDB], limit: int = 10, offset: int = 0, category_list: Optional[List[str]] = None) -> List[ProductRead]:
    if not space or not style:
        raise HTTPException(status_code=400, detail="Space and style parameters are required")

    space_doc = await spaces_collection.find_one({"name": space})
    style_doc = await styles_collection.find_one({"name": style})

    if not space_doc or not style_doc:
        raise HTTPException(status_code=404, detail="Space or style not found")

    space_id = str(space_doc["_id"])
    style_id = str(style_doc["_id"])

    if user is None:
        return await get_top_products(space_id, style_id, limit, offset, category_list)

    user_history = await user_history_service.get_user_history(str(user._id))

    if not user_history:
        return await get_top_products(space_id, style_id, limit, offset, category_list)

    liked_product_ids = [h.product_id for h in user_history]
    liked_products = [await products_service.get_product(pid) for pid in liked_product_ids]
    liked_products = [p for p in liked_products if p is not None]

    if not liked_products:
        raise HTTPException(status_code=404, detail="No valid liked products found")

    liked_dicts = [p.model_dump() for p in liked_products]
    liked_matrix, vectorizer = vectorize_products(liked_dicts)
    user_vector = np.asarray(liked_matrix.mean(axis=0)).reshape(1, -1)

    filtered_products = await products_service.get_products_by_space_and_style(space_id, style_id, category_list)
    if not filtered_products:
        raise HTTPException(status_code=404, detail="No products found for selected space and style")

    filtered_texts = [
        f"{p['name']} {p['description']} {p.get('category', '')}".lower()
        for p in filtered_products
    ]
    filtered_matrix = vectorizer.transform(filtered_texts)

    similarity_scores = cosine_similarity(user_vector, filtered_matrix).flatten()
    quality_scores = [p.get("rating", 0) * p.get("review_count", 0) for p in filtered_products]
    quality_scores_normalized = normalize_scores(quality_scores)


    alpha, beta = 0.70, 0.40
    final_scores = [
        alpha * sim + beta * qual
        for sim, qual in zip(similarity_scores, quality_scores_normalized)
    ]

    sorted_products = [
        p for _, p in sorted(zip(final_scores, filtered_products), key=lambda pair: pair[0], reverse=True)
    ]

    paginated = sorted_products[offset:offset + limit]
    return [products_service.from_mongo(p, ProductRead) for p in paginated]


async def get_top_products(space: str, style: str, limit: int, offset: int = 0, categories: Optional[List[str]] = None) -> List[ProductRead]:
    filtered_products = await products_service.get_products_by_space_and_style(space, style, categories)
    if not filtered_products:
        raise HTTPException(status_code=404, detail="No products found for selected space and style")

    def quality_score(p):
        return p.get("rating", 0) * p.get("review_count", 0)

    sorted_products = sorted(filtered_products, key=quality_score, reverse=True)
    paginated = sorted_products[offset:offset + limit]
    return [products_service.from_mongo(p, ProductRead) for p in paginated]

def normalize_scores(values):
    min_v, max_v = min(values), max(values)
    return [(v - min_v) / (max_v - min_v) if max_v != min_v else 0 for v in values]

