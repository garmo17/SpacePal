import asyncio
from backend.api.services.products import list_products, update_product
from backend.api.ml.categorization import categorize_product_by_description
from backend.api.schemas.products import ProductUpdate
from backend.api.services.categorization_service import load_embeddings

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
            category_embeddings, space_embeddings, style_embeddings, space_names, style_names = await load_embeddings()
            category, spaces, styles = categorize_product_by_description(product.description,
                                                                        category_embeddings,
                                                                        space_embeddings,
                                                                        style_embeddings,
                                                                        space_names,
                                                                        style_names,
                                                                        n_spaces=3,
                                                                        n_styles=3)
            product.category = category
            product.spaces = spaces
            product.styles = styles

            product_update = ProductUpdate(
                name=product.name,
                description=product.description,
                price=product.price,
                purchase_link=product.purchase_link,
                image_url=product.image_url,
                category=product.category,
                spaces=product.spaces,
                styles=product.styles
            )

            await update_product(product.id, product_update)
            print(f"✔ Producto actualizado: {product.name} ({product.id})")

if __name__ == "__main__":
    asyncio.run(main())
