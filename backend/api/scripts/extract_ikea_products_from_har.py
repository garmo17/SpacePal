import json
import pandas as pd
from bs4 import BeautifulSoup
import requests
from backend.api.ml.categorization import categorize_product_by_description

# === CONFIGURACIÓN ===
input_har = "backend/api/data/www.ikea.com.har"
output_excel = "backend/api/output/products.xlsx"
base_url = "https://www.ikea.com"

# === CARGAR ARCHIVO HAR ===
with open(input_har, 'r', encoding='utf-8') as f:
    har_data = json.load(f)

productos = []
visited_urls = set()

for entry in har_data["log"]["entries"]:
    url = entry["request"]["url"]
    if "shoppable-fragment" not in url or url in visited_urls:
        continue

    visited_urls.add(url)

    # Obtener contenido HTML
    content = entry.get("response", {}).get("content", {}).get("text", "")
    if not content:
        try:
            content = requests.get(url).text
        except:
            continue

    soup = BeautifulSoup(content, 'html.parser')

    # Buscar bloque principal
    div = soup.select_one(".pip-shoppable-price-package")
    if not div:
        continue

    name = div.get("data-product-name", "").strip()

    # Descripción del producto
    desc_tag = soup.find("span", class_="pip-header-section__description-text")
    description_1 = desc_tag.get_text(strip=True) if desc_tag else ""

    # Precio
    price_int = soup.find("span", class_="pip-price__integer")
    price_dec = soup.find("span", class_="pip-price__decimal")
    price_str = f"{price_int.get_text(strip=True)}{price_dec.get_text(strip=True)}" if price_int and price_dec else ""
    try:
        price = float(price_str)
    except:
        price = None

    # Enlace al producto
    link_tag = soup.find("a", class_="pip-shoppable-price-package__link")
    purchase_link = link_tag["href"] if link_tag else ""

    # Cargar HTML del producto completo para obtener imagen
    try:
        product_html = requests.get(purchase_link).text
        product_soup = BeautifulSoup(product_html, 'html.parser')
        image_tag = product_soup.find("img", class_="pip-image")
        image_url = image_tag["src"] if image_tag else ""
        extended_descriptions = product_soup.find_all("p", class_="pip-product-details__paragraph")
        full_description = description_1 + " " + " ".join([desc.get_text(strip=True) for desc in extended_descriptions])
    except:
        image_url = ""
        full_description = description_1

    # Categoría
    category = categorize_product_by_description(full_description)

    # Guardar producto
    productos.append({
        "name": name,
        "description": full_description,
        "price": price,
        "purchase_link": purchase_link,
        "image_url": image_url,
        "category": category
    })

    print({
        "name": name,
        "description": full_description,
        "price": price,
        "purchase_link": purchase_link,
        "image_url": image_url,
        "category": category
    })

# === GUARDAR EN EXCEL ===
df = pd.DataFrame(productos)
df.to_excel(output_excel, index=False)
print(f"✅ Guardado: {output_excel} ({len(df)} productos)")


