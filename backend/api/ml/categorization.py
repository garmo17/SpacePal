from sentence_transformers import SentenceTransformer, util
from backend.api.services.spaces import get_spaces
from backend.api.services.styles import get_styles

model = SentenceTransformer("all-mpnet-base-v2")

# Candidatos base
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

all_spaces = get_spaces()
space_labels = [f"{space.name.lower()}: {space.description.lower()}" for space in all_spaces]
space_names = [space.name for space in all_spaces]

all_styles = get_styles()
style_labels = [f"{style.name.lower()}: {style.description.lower()}" for style in all_styles]
style_names = [style.name for style in all_styles]

category_embeddings = model.encode(category_labels, convert_to_tensor=True)
space_embeddings = model.encode(space_labels, convert_to_tensor=True)
style_embeddings = model.encode(style_labels, convert_to_tensor=True)

def get_top_k_labels(description: str, candidates: list[str], embeddings, k=3) -> list[str]:
    description_embedding = model.encode(description, convert_to_tensor=True)
    cosine_scores = util.cos_sim(description_embedding, embeddings)[0]
    top_results = cosine_scores.topk(k=k)
    return [candidates[i] for i in top_results.indices]

def categorize_product_by_description(description: str):
    category = get_top_k_labels(description, category_labels, category_embeddings, k=1)[0]
    spaces = get_top_k_labels(description, space_names, space_embeddings, k=3)
    styles = get_top_k_labels(description, style_names, style_embeddings, k=3)
    return category, spaces, styles
