import hashlib
import secrets
import time
from bson import ObjectId
from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from ..settings import JWT_SECRET_KEY, JWT_ALGORITHM, ASYNC_MONGODB_DB


pl_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2 = OAuth2PasswordBearer(tokenUrl="/login")

def rate_limit_func(request: Request):
    return request.headers.get("x-api-key")

def create_access_token(user_id: str, expires_mins: int = 15) -> str:
    """Create access token for auth-based endpoints"""
    current_time = time.time()
    
    payload = {
        "sub": user_id,
        "exp": current_time + (expires_mins * 60),
        "iat": current_time
    }
    token = jwt.encode(payload, key=JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

async def get_current_user(token: str = Depends(oauth2)):
    try:
        payload = jwt.decode(token, key=JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid token")
    
    user_collection = ASYNC_MONGODB_DB["users"]
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return HTTPException(404, "User not found")
    return user

def create_api_key():
    """Generate an API key and return it with its hash."""
    key = secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    return key, key_hash

async def require_api_key(x_api_key: str = Header(...)):
    key_collection = ASYNC_MONGODB_DB["api_keys"]
    api_key = await key_collection.find_one({"key_hash": hashlib.sha256(x_api_key.encode()).hexdigest()})
    if not api_key:
        raise HTTPException(401, "Invalid API key")
    return api_key["user_id"]
