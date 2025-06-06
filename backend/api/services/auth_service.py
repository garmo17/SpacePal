from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from backend.api.models.users import UserDB
from backend.api.db.database import users_collection
from dotenv import load_dotenv
from bson import ObjectId
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(username: str) -> Optional[UserDB]:
    user_dict = await users_collection.find_one({"username": username})
    if user_dict:
        return UserDB(
            username=user_dict["username"],
            email=user_dict["email"],
            password=user_dict["password"],
            _id=user_dict["_id"]
        )
    return None


async def get_user_by_id(user_id: str) -> Optional[UserDB]:
    user_dict = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user_dict:
        return UserDB(
            username=user_dict["username"],
            email=user_dict["email"],
            password=user_dict["password"],
            _id=user_dict["_id"]
        )
    return None


async def authenticate_user(username: str, password: str) -> Optional[UserDB]:
    user = await get_user(username)
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme_optional)) -> Optional[UserDB]:
    if not token:
        return None
    try:
        return await get_current_user(token)
    except HTTPException:
        return None