from backend.api.ml.categorization import categorize_product_by_description, model, category_labels
from unittest.mock import patch
import pytest

@pytest.mark.asyncio
async def test_categorize_product_by_description_with_more_options():
    description = "Rustic wooden chair for outdoor terrace, perfect for relaxing in the garden."

    space_names = ["terrace", "garden", "dining room", "living room", "office", "bedroom"]
    space_labels = [
        "terrace: outdoor space to relax",
        "garden: green outdoor area",
        "dining room: place to eat with family and friends",
        "living room: common area for gatherings and relaxation",
        "office: workspace for productivity",
        "bedroom: place for rest and sleep"
    ]

    style_names = ["rustic", "nordic", "minimalist", "industrial", "bohemian", "classic"]
    style_labels = [
        "rustic: wood, nature, and warmth",
        "nordic: clean lines and light tones",
        "minimalist: simplicity and order",
        "industrial: metal and concrete with urban touches",
        "bohemian: mix of textures and colors",
        "classic: elegance and tradition"
    ]

    category_embeddings = model.encode(category_labels, convert_to_tensor=True)
    space_embeddings = model.encode(space_labels, convert_to_tensor=True)
    style_embeddings = model.encode(style_labels, convert_to_tensor=True)

    with patch("backend.api.ml.categorization.get_ids_from_names") as mock_get_ids:
        mock_get_ids.side_effect = lambda names, collection: [f"fake_id_{name}" for name in names]

        category, spaces, styles = await categorize_product_by_description(
            description,
            category_embeddings,
            space_embeddings,
            style_embeddings,
            space_names,
            style_names
        )

    print("🔎 Category:", category)
    print("📍 Spaces (Top 3):", spaces)
    print("🎨 Styles (Top 3):", styles)

    assert isinstance(category, str)
    assert isinstance(spaces, list) and len(spaces) == 3
    assert isinstance(styles, list) and len(styles) == 3
