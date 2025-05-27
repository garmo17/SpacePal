from fastapi import APIRouter, status, HTTPException, Depends
from backend.api.dependencies.auth import get_current_user
from backend.api.schemas.products import ProductRead
from backend.api.services import user_history as user_history_service
from backend.api.services import products as products_service
from backend.api.ml.recomender import vectorize_products
from typing import List
from sklearn.metrics.pairwise import cosine_similarity
from backend.api.models.users import UserDB
import numpy as np

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/user", response_model=List[ProductRead], status_code=status.HTTP_200_OK)
async def personalized_recommendations(space: str, style: str, limit: int = 10, current_user: UserDB = Depends(get_current_user)):
    # 1️⃣ Recuperar historial de usuario
    user_history = await user_history_service.get_user_history(str(current_user._id))

    # 2️⃣ Si no hay historial → devolver productos mejor rankeados por espacio y estilo
    if not user_history:
        filtered_products = await products_service.get_products_by_space_and_style(space, style)

        if not filtered_products:
            raise HTTPException(status_code=404, detail="No products found for selected space and style")
        
        def quality_score(p):
            return p.get("rating", 0) * p.get("review_count", 0)

        sorted_products = sorted(filtered_products, key=quality_score, reverse=True)
        return [products_service.from_mongo(p, ProductRead) for p in sorted_products[:limit]]

    # 3️⃣ Si hay historial → obtener productos del historial
    liked_product_ids = [h.product_id for h in user_history]
    liked_products = [await products_service.get_product(pid) for pid in liked_product_ids]
    liked_products = [p for p in liked_products if p is not None]
    if not liked_products:
        raise HTTPException(status_code=404, detail="No valid liked products found")

    # 4️⃣ Vectoriza historial (usa vectorize_products que recibe lista de dicts/modelos)
    liked_dicts = [p.model_dump() for p in liked_products]
    liked_matrix, vectorizer = vectorize_products(liked_dicts)

    # 5️⃣ Calcula vector medio (perfil del usuario)
    user_vector = np.asarray(liked_matrix.mean(axis=0)).reshape(1, -1)

    # 6️⃣ Filtra productos por espacio y estilo
    filtered_products = await products_service.get_products_by_space_and_style(space, style)

    if not filtered_products:
        raise HTTPException(status_code=404, detail="No products found for selected space and style")

    # 7️⃣ Usa el mismo vectorizador para transformar productos filtrados
    filtered_texts = [
        f"{p['name']} {p['description']} {p.get('category', '')}".lower()
        for p in filtered_products
    ]
    filtered_matrix = vectorizer.transform(filtered_texts)

    # 8️⃣ Calcula similitud coseno (usuario vs cada producto)
    similarity_scores = cosine_similarity(user_vector, filtered_matrix).flatten()

    # 9️⃣ Calcula calidad (rating * review_count normalizado)
    quality_scores = [p.get("rating", 0) * p.get("review_count", 0) for p in filtered_products]
    quality_scores_normalized = normalize(quality_scores)

    # 🔟 Combina scores
    alpha, beta = 0.65, 0.35  # Ajusta los pesos si quieres más personalización o calidad
    final_scores = [
        alpha * sim + beta * qual
        for sim, qual in zip(similarity_scores, quality_scores_normalized)
    ]

    # 🔟+1 Ordena productos por score final
    sorted_products = [
        p for _, p in sorted(zip(final_scores, filtered_products), key=lambda pair: pair[0], reverse=True)
    ]

    # 🔟+2 Devuelve resultados como ProductRead
    return [products_service.from_mongo(p, ProductRead) for p in sorted_products[:limit]]

def normalize(values):
    min_v, max_v = min(values), max(values)
    return [(v - min_v) / (max_v - min_v) if max_v != min_v else 0 for v in values]
