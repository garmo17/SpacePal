from backend.api.db.database import products_collection, spaces_collection, styles_collection
import asyncio
from bson import ObjectId

async def get_ids_from_names(names, collection):
    ids = []
    for name in names:
        doc = await collection.find_one({"name": name})
        if doc:
            ids.append(str(doc["_id"]))
    return ids

async def main():
    products = products_collection.find({
        "$or": [
            {"spaces": {"$exists": True, "$ne": []}},
            {"styles": {"$exists": True, "$ne": []}}
        ]
    })

    async for product in products:
        spaces = product.get("spaces", [])
        styles = product.get("styles", [])

        # 🔥 Convertir nombres a IDs
        spaces_ids = await get_ids_from_names(spaces, spaces_collection)
        styles_ids = await get_ids_from_names(styles, styles_collection)

        # Actualizar el producto en la colección
        await products_collection.update_one(
            {"_id": product["_id"]},
            {
                "$set": {
                    "spaces": spaces_ids,
                    "styles": styles_ids
                }
            }
        )

        print(f"Updated product {str(product['_id'])} with spaces: {spaces_ids} and styles: {styles_ids}")

if __name__ == "__main__":
    asyncio.run(main())
