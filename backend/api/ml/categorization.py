from transformers import pipeline

# Cargamos el pipeline solo una vez
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def categorize_product_by_description(description: str) -> str:
    candidate_labels = [
    "lighting",
    "decoration and mirrors",
    "storage and organization",
    "tables and chairs",
    "desks and desk chairs",
    "home textiles",
    "sofas and armchairs",
    "flooring, rugs and mats",
    "outdoor furniture",
    "plants and gardening",
    "beds and mattresses",
    "smart home and technology",
    "kitchen and tableware",
    ]
    result = classifier(description, candidate_labels)
    return result["labels"][0]  

# Output: 'almacenamiento'
print(categorize_product_by_description("Modern floor lamp"))  # Ejemplo de uso