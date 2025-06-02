from backend.api.ml.categorization import categorize_product_by_description, model, category_labels
from backend.api.db.database import products_collection

async def test_categorize_product_by_description_with_more_options():
    description = "Silla de madera rústica para terraza exterior, ideal para relajarse en el jardín"

    # Añadimos más espacios de prueba
    space_names = ["terraza", "jardín", "comedor", "salón", "oficina", "dormitorio"]
    space_labels = [
        "terraza: espacio exterior para relajarse",
        "jardín: zona verde al aire libre",
        "comedor: lugar para comer con familia y amigos",
        "salón: zona común para reuniones y descanso",
        "oficina: espacio para trabajo y productividad",
        "dormitorio: zona para descansar y dormir"
    ]

    # Añadimos más estilos de prueba
    style_names = ["rústico", "nórdico", "minimalista", "industrial", "bohemio", "clásico"]
    style_labels = [
        "rústico: madera, naturaleza y calidez",
        "nórdico: líneas limpias y tonos claros",
        "minimalista: simplicidad y orden",
        "industrial: metal y hormigón con toques urbanos",
        "bohemio: mezcla de texturas y colores",
        "clásico: elegancia y tradición"
    ]

    # Calculamos embeddings
    category_embeddings = model.encode(category_labels, convert_to_tensor=True)
    space_embeddings = model.encode(space_labels, convert_to_tensor=True)
    style_embeddings = model.encode(style_labels, convert_to_tensor=True)

    # Llamamos a la función
    category, spaces, styles = await categorize_product_by_description(
        description,
        category_embeddings,
        space_embeddings,
        style_embeddings,
        space_names,
        style_names
    )


    print("🔎 Categoría:", category)
    print("📍 Espacios (Top 3):", spaces)
    print("🎨 Estilos (Top 3):", styles)

    assert isinstance(category, str)
    assert isinstance(spaces, list) and len(spaces) == 3
    assert isinstance(styles, list) and len(styles) == 3
