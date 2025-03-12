from schemas.products import Product


product_list = [
    Product(id=1, name="Rick", description="Rick Sanchez", price=1000.0, url="www.rick.com", image_url="www.rick.com", category="cartoon"),
    Product(id=2, name="Morty", description="Morty Smith", price=1000.0, url="www.morty.com", image_url="www.morty.com", category="cartoon"),
    Product(id=3, name="Summer", description="Summer Smith", price=1000.0, url="www.summer.com", image_url="www.summer.com", category="cartoon")
]


async def list_products(skip: int = 0, limit: int = 10):
    return product_list[skip : skip + limit]

async def get_product(id: int):
    return next((product for product in product_list if product.id == id), None)

async def create_product(product_data: Product):
    if any(p.id == product_data.id for p in product_list):
        return None
    product_list.append(product_data)
    return product_data

async def delete_product(id: int):
    product = await get_product(id)
    if product:
        product_list.remove(product)
        return product
    return None

async def update_product(id: int, updated_data: Product):
    product = await get_product(id)
    if product:
        product.name = updated_data.name
        product.description = updated_data.description
        product.price = updated_data.price
        product.purchase_link = updated_data.purchase_link
        product.category = updated_data.category
        return product
    return None
