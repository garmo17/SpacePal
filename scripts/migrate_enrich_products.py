import asyncio
from backend.api.services.products import list_products, update_product
from backend.api.ml.categorization import categorize_product_by_description

async def main():
    products = await list_products()
    print(f"🔍 Total productos encontrados: {len(products)}")

    for product in products:
        needs_update = (
            not product.category or
            not product.spaces or
            not product.styles
        )
        if needs_update:
            category, spaces, styles = categorize_product_by_description(product.description)
            product.category = category
            product.spaces = spaces
            product.styles = styles

            await update_product(product.id, product)
            print(f"✔ Producto actualizado: {product.name} ({product.id})")

if __name__ == "__main__":
    asyncio.run(main())
