from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File, Response, Request
import json
from backend.api.dependencies.auth import is_admin
from backend.api.services import products as products_service
from backend.api.schemas.products import *
from typing import List



router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[ProductRead], status_code=status.HTTP_200_OK)
async def get_products(request: Request, response: Response):
    range_param = request.query_params.get('range')
    if range_param:
        range_values = json.loads(range_param)  
        skip = range_values[0]
        limit = range_values[1] - range_values[0] + 1
    else:
        skip = 0
        limit = 10

    products, total = await products_service.list_products(skip, limit)
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")
    response.headers["Content-Range"] = f"0-{skip + len(products) - 1}/{total}"
    return products

@router.get("/{id}", response_model=ProductRead, status_code=status.HTTP_200_OK)
async def get_product(id: str):
    product = await products_service.get_product(id)  
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, current_user: str = Depends(is_admin), n_spaces: int = 3, n_styles: int = 3):
    created_product = await products_service.create_product(product_data, n_spaces=n_spaces, n_styles=n_styles)  
    if isinstance(created_product, dict) and "error" in created_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=created_product["error"])
    if not created_product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product already exists")
    return created_product

@router.post("/bulk", response_model=ProductsBulkResponse, status_code=status.HTTP_201_CREATED)
async def create_products(products_data: List[ProductCreate], current_user: str = Depends(is_admin), n_spaces: int = 3, n_styles: int = 3):
    results = await products_service.create_products(products_data, n_spaces=n_spaces, n_styles=n_styles)
    if not results.get("created"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="All products already exist, or category not aplicable")
    return results

@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_product(id: str, current_user: str = Depends(is_admin)):
    success = await products_service.delete_product(id)  
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return {"message": "Product deleted successfully"}

@router.delete("/", status_code=status.HTTP_200_OK)
async def delete_all_products(current_user: str = Depends(is_admin)):
    success = await products_service.delete_all_products()  
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete products")
    return {"message": "All products deleted successfully"}

@router.put("/{id}", response_model=ProductRead, status_code=status.HTTP_200_OK)
async def update_product(id: str, product_data: ProductUpdate, current_user: str = Depends(is_admin)):
    updated_product = await products_service.update_product(id, product_data)  
    if isinstance(updated_product, dict) and "error" in updated_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=updated_product["error"])
    if not updated_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return updated_product

@router.post("/import")
async def import_products(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .xlsx")
    try:
        contents = await file.read()
        result = await products_service.import_products_from_excel(contents)
        return {
            "inserted": result["inserted"],
            "skipped": result["skipped"],
            "total": result["total"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")
    
@router.get("/{id}/recomendations", response_model=List[ProductRead], status_code=status.HTTP_200_OK)
async def get_product_recommendations(id: str, top_n: int = 5):
    try:
        result = await products_service.get_product_recommendations(id, top_n)
        if result is None:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{id}/reviews", response_model=List[ProductReview], status_code=status.HTTP_200_OK)
async def get_product_reviews(id: str):
    reviews = await products_service.get_product_reviews(id)  
    if not reviews:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return reviews

@router.post("/products/{id}/reviews", response_model=ProductReview)
async def add_product_review(id: str, review: ProductReviewCreate):
    review = await products_service.add_product_review(id, review)  
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return review
    
    
