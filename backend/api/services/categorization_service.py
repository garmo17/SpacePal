from backend.api.services.spaces import list_spaces
from backend.api.services.styles import list_styles
from backend.api.ml.categorization import model, category_labels

async def load_embeddings():
    all_spaces, _ = await list_spaces(limit=1000)
    space_labels = [f"{space.name.lower()} {space.description.lower()}" for space in all_spaces]
    space_names = [space.name for space in all_spaces]

    all_styles, _ = await list_styles(limit=1000)
    style_labels = [f"{style.name.lower()} {style.description.lower()}" for style in all_styles]
    style_names = [style.name for style in all_styles]

    category_embeddings = model.encode(category_labels, convert_to_tensor=True)
    space_embeddings = model.encode(space_labels, convert_to_tensor=True)
    style_embeddings = model.encode(style_labels, convert_to_tensor=True)

    return category_embeddings, space_embeddings, style_embeddings, space_names, style_names
