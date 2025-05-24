from unittest.mock import patch
from backend.api.ml.categorization import categorize_product_by_description

def test_categorize_product_by_description_with_mocked_spaces_and_styles():
    description = "Silla de madera para jardín rústico, ideal para terraza exterior"

    with patch("backend.api.ml.categorization.get_spaces") as mock_spaces, \
         patch("backend.api.ml.categorization.get_styles") as mock_styles:

        mock_spaces.return_value = [
            type("MockSpace", (), {"name": "terraza", "description": "espacio exterior para relajarse"})(),
            type("MockSpace", (), {"name": "jardín", "description": "zona verde al aire libre"})(),
        ]

        mock_styles.return_value = [
            type("MockStyle", (), {"name": "rústico", "description": "madera, naturaleza y calidez"})(),
            type("MockStyle", (), {"name": "nórdico", "description": "líneas limpias y tonos claros"})(),
        ]

        category, spaces, styles = categorize_product_by_description(description)

        print("Categoría:", category)
        print("Espacios:", spaces)
        print("Estilos:", styles)

        assert isinstance(category, str)
        assert isinstance(spaces, list) and len(spaces) > 0
        assert isinstance(styles, list) and len(styles) > 0
