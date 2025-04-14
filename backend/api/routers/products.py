from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File
from backend.api.dependencies.auth import is_admin
from backend.api.services import products as products_service
from backend.api.schemas.products import ProductRead, ProductCreate, ProductUpdate



router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=list[ProductRead], status_code=status.HTTP_200_OK)
async def get_products(skip: int = 0, limit: int = 10):
    products = await products_service.list_products(skip, limit)  
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")
    return products

@router.get("/{id}", response_model=ProductRead, status_code=status.HTTP_200_OK)
async def get_product(id: str):
    product = await products_service.get_product(id)  
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, current_user: str = Depends(is_admin)):
    created_product = await products_service.create_product(product_data)  
    if not created_product:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product already exists")
    return created_product

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
    if not updated_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return updated_product

@router.post("/import")
async def import_products(file: UploadFile = File(...)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .xlsx")
    try:
        contents = await file.read()
        count = await products_service.import_products_from_excel(contents)
        return {"inserted": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")