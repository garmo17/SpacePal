from fastapi import APIRouter, FastAPI
from backend.api.routers import recommendations, users, spaces, products, styles, auth, user_history
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API",
    description="Una API con FastAPI con entidades de usuarios, espacios, productos y estilos",
    version="1.0.0") 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost", "http://localhost:3000", "https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range"],
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(users.router)
api_router.include_router(spaces.router)
api_router.include_router(products.router)
api_router.include_router(styles.router)
api_router.include_router(auth.router)
api_router.include_router(user_history.router)
api_router.include_router(recommendations.router)

@api_router.get("/")
def root():
    return {"message": "Bienvenido a mi API 🚀"}

app.include_router(api_router)

