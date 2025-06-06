from sentence_transformers import SentenceTransformer, util
from typing import List
from backend.api.db.database import spaces_collection, styles_collection

model = SentenceTransformer("all-mpnet-base-v2")

category_labels = [
    "lighting",
    "home decor and accessories",
    "storage and organization",
    "tables and chairs",
    "desks and desk chairs",
    "home textiles",
    "sofas and armchairs",
    "flooring, rugs and mats",
    "outdoor",
    "plants and gardening",
    "beds and mattresses",
    "smart home and technology",
    "kitchen and tableware",
]

def get_top_k_labels(description: str, candidates: List[str], embeddings, k=3) -> List[str]:
    description_embedding = model.encode(description, convert_to_tensor=True)
    cosine_scores = util.cos_sim(description_embedding, embeddings)[0]
    top_results = cosine_scores.topk(k=k)
    return [candidates[i] for i in top_results.indices]

async def categorize_product_by_description(
    description: str,
    category_embeddings,
    space_embeddings,
    style_embeddings,
    space_names,
    style_names,
    n_spaces=3,
    n_styles=3
):
    category = get_top_k_labels(description, category_labels, category_embeddings, k=1)[0]
    spaces = get_top_k_labels(description, space_names, space_embeddings, k=n_spaces)
    styles = get_top_k_labels(description, style_names, style_embeddings, k=n_styles)

    spaces_ids = await get_ids_from_names(spaces, spaces_collection)
    styles_ids = await get_ids_from_names(styles, styles_collection)
    return category, spaces_ids, styles_ids


async def get_ids_from_names(names: List[str], collection):
    ids = []
    for name in names:
        doc = await collection.find_one({"name": name})
        if doc:
            ids.append(str(doc["_id"]))
    return ids
