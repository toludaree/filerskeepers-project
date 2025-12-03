import hashlib
import secrets
import time
from bson import ObjectId
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Header, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import ConnectionFailure
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..settings import (
    JWT_ALGORITHM, JWT_SECRET_KEY, MONGODB_CONNECTION_URI, MONGODB_DB,
    MONGODB_USERS_COLLECTION, MONGODB_API_KEYS_COLLECTION,
)
from .common import setup_logger


logger = setup_logger("api", add_file_handler=False, use_uvicorn_format=True)

def rate_limit_func(request: Request):
    return request.headers.get("x-api-key")

auth_limiter = Limiter(key_func=get_remote_address)
api_limiter = Limiter(key_func=rate_limit_func)

pl_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")  # passlib context
oauth2 = OAuth2PasswordBearer(tokenUrl="/login")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan. Used to initialize and close database"""
    app.mongodb_client = None
    try:
        app.mongodb_client = AsyncMongoClient(
            MONGODB_CONNECTION_URI,
            timeoutMS=5000
        )

        await app.mongodb_client.admin.command("ping")
        app.db = app.mongodb_client[MONGODB_DB]
        logger.info("Database connected")

        yield

    except ConnectionFailure:
        logger.error("MongoDB connection failed")
        raise

    finally:
        if app.mongodb_client:
            await app.mongodb_client.close()
            logger.info("Database disconnected")

async def get_db(request: Request):
    """Database dependency for endpoints."""
    return request.app.db

def create_access_token(user_id: str, expires_mins: int = 15) -> str:
    """Create access token for auth-based endpoints."""
    current_time = time.time()
    
    payload = {
        "sub": user_id,
        "exp": current_time + (expires_mins * 60),
        "iat": current_time
    }
    token = jwt.encode(payload, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

async def get_current_user(
    db: AsyncDatabase = Depends(get_db),
    token: str = Depends(oauth2)
):
    """Dependency for auth endpoints."""
    try:
        payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, detail="Invalid token")
    
    user_collection = db[MONGODB_USERS_COLLECTION]
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return HTTPException(404, detail="User not found")
    return user

def create_api_key():
    """Generate an API key and return it with its hash."""
    key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    return key, key_hash

async def require_api_key(
    db: AsyncDatabase = Depends(get_db),
    x_api_key: str = Header(...)
):
    """Dependency for book endpoints."""
    key_collection = db[MONGODB_API_KEYS_COLLECTION]

    api_key = await key_collection.find_one(
        {"key_hash": hashlib.sha256(x_api_key.encode()).hexdigest()}
    )
    if not api_key:
        raise HTTPException(401, detail="Invalid API key")
    return api_key["user_id"]
