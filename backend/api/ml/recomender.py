from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
from backend.api.schemas.products import ProductRead

def vectorize_texts(products: List[Dict]) -> Tuple:
    corpus = [
        f"{p['name']} {p['description']} {p['category']}".lower()
        for p in products
    ]
    vectorizer = TfidfVectorizer(stop_words="spanish")
    tfidf_matrix = vectorizer.fit_transform(corpus)
    return tfidf_matrix, vectorizer

def recommend_by_cosine_similarity(product_id: str, products: List[ProductRead], top_n: int = 5) -> List[ProductRead]:
    tfidf_matrix, _ = vectorize_texts([p.dict() for p in products])
    index_map = {str(p.id): idx for idx, p in enumerate(products)}  # Asegura que id sea str

    if product_id not in index_map:
        raise ValueError(f"Product ID {product_id} not found in the product list.")
    
    product_index = index_map[product_id]
    similarity_scores = cosine_similarity(tfidf_matrix[product_index], tfidf_matrix).flatten()
    similar_indexes = similarity_scores.argsort()[::-1][1:top_n+1]
    return [products[i] for i in similar_indexes]
