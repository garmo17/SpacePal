import json
import pandas as pd
from bs4 import BeautifulSoup
import requests
import random
import asyncio
from backend.api.ml.categorization import categorize_product_by_description
from backend.api.services.categorization_service import load_embeddings  # ✅ Usa la función ya existente

# === CONFIGURACIÓN ===
input_har = "backend/api/data/www.ikea.com.har"
output_excel = "backend/api/output/products.xlsx"
base_url = "https://www.ikea.com"

async def main():
    # 1️⃣ Carga embeddings usando la función centralizada
    category_embeddings, space_embeddings, style_embeddings, space_names, style_names = await load_embeddings()

    # 2️⃣ Carga archivo HAR
    with open(input_har, 'r', encoding='utf-8') as f:
        har_data = json.load(f)

    productos = []
    visited_urls = set()

    # 3️⃣ Procesa entradas del HAR
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

        # Nombre
        div = soup.select_one(".pip-shoppable-price-package")
        if not div:
            continue
        name = div.get("data-product-name", "").strip()

        # Descripción
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

        # Cargar HTML del producto completo para obtener imagen y descripción extendida
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

        # Categoría, espacios y estilos
        category, spaces, styles = await categorize_product_by_description(
            full_description,
            category_embeddings,
            space_embeddings,
            style_embeddings,
            space_names,
            style_names
        )

        # Guarda producto con campos extra
        productos.append({
            "name": name,
            "description": full_description,
            "price": price,
            "purchase_link": purchase_link,
            "image_url": image_url,
            "category": category,
            "spaces": spaces,
            "styles": styles,
            "rating": round(random.uniform(3.0, 5.0), 2),
            "review_count": random.randint(0, 10),
            "reviews": []
        })

        # Debug de consola
        print({
            "name": name,
            "description": full_description,
            "price": price,
            "purchase_link": purchase_link,
            "image_url": image_url,
            "category": category,
            "spaces": spaces,
            "styles": styles,
            "rating": round(productos[-1]["rating"], 2),
            "review_count": productos[-1]["review_count"],
            "reviews": productos[-1]["reviews"]
        })

    # 4️⃣ Guarda a Excel
    df = pd.DataFrame(productos)
    df.to_excel(output_excel, index=False)
    print(f"✅ Guardado: {output_excel} ({len(df)} productos)")

if __name__ == "__main__":
    asyncio.run(main())
