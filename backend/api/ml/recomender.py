from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
from backend.api.schemas.products import ProductRead
from backend.api.services.spaces import get_space
from backend.api.services.styles import get_style


def vectorize_products(products: List[Dict]) -> Tuple:
    corpus = [
        f"{p['name']} {p['description']} {p['category']}".lower()
        for p in products
    ]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)
    return tfidf_matrix, vectorizer

def vectorize_texts(texts: List[str]) -> Tuple:
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(texts)
    return tfidf_matrix, vectorizer


async def recommend_by_cosine_similarity(product_id: str, products: List[ProductRead], top_n: int = 5) -> List[ProductRead]:
    corpus = [await build_product_corpus(p) for p in products]

    tfidf_matrix, _ = vectorize_texts(corpus)
    index_map = {str(p.id): idx for idx, p in enumerate(products)}

    if product_id not in index_map:
        raise ValueError(f"Product ID {product_id} not found in the product list.")
    
    product_index = index_map[product_id]
    similarity_scores = cosine_similarity(tfidf_matrix[product_index], tfidf_matrix).flatten()
    similar_indexes = similarity_scores.argsort()[::-1][1:top_n+1]
    return [products[i] for i in similar_indexes]


async def build_product_corpus(p: ProductRead) -> str:
    space_names = []
    style_names = []

    for space_id in p.spaces or []:
        space = await get_space(space_id)
        if space:
            space_names.append(space.name)

    for style_id in p.styles or []:
        style = await get_style(style_id)
        if style:
            style_names.append(style.name)

    return f"{p.name} {p.description} {p.category} {' '.join(space_names)} {' '.join(style_names)}".lower()
