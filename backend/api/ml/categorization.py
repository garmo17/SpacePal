from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-mpnet-base-v2")

candidate_labels = [
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

label_embeddings = model.encode(candidate_labels, convert_to_tensor=True)

def categorize_product_by_description(description: str) -> str:
    description_embedding = model.encode(description, convert_to_tensor=True)
    cosine_scores = util.cos_sim(description_embedding, label_embeddings)[0]
    best_index = cosine_scores.argmax().item()
    return candidate_labels[best_index]
