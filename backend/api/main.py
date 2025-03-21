from fastapi import APIRouter, FastAPI
from routers import users, spaces, products, styles

app = FastAPI(title="API",
    description="Una API con FastAPI con entidades de usuarios, espacios, productos y estilos",
    version="1.0.0") 

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(users.router)
api_router.include_router(spaces.router)
api_router.include_router(products.router)
api_router.include_router(styles.router)

@api_router.get("/")
def root():
    return {"message": "Bienvenido a mi API 🚀"}

app.include_router(api_router)

