from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.asynchronous.database import AsyncDatabase

from ...settings import (
    AUTH_RATE_LIMIT, MONGODB_USERS_COLLECTION, MONGODB_API_KEYS_COLLECTION
)
from ...utils.api import (
    auth_limiter, create_access_token, create_api_key, get_current_user,
    get_db, logger, pl_ctx
)
from ..models.auth import GenerateApiKey, Login, SignUp, UserData


router = APIRouter()

@router.post(
    "/signup",
    tags=["auth"], response_model=SignUp
)
@auth_limiter.limit(AUTH_RATE_LIMIT)
async def signup(
    request: Request,
    user_data: UserData,
    db: AsyncDatabase = Depends(get_db)
):
    """Create new API user"""
    try:
        user_collection = db[MONGODB_USERS_COLLECTION]

        if await user_collection.find_one({"email": user_data.email}):
            raise HTTPException(400, detail="User already exists")
        
        await user_collection.insert_one({
            "email": user_data.email,
            "password": pl_ctx.hash(user_data.password)
        })
        return {
            "message": "User created"
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error: {repr(exc)}")
        raise HTTPException(500, detail=str(exc))
    
@router.post(
    "/login",
    tags=["auth"], response_model=Login
)
@auth_limiter.limit(AUTH_RATE_LIMIT)
async def login(
    request: Request,
    user_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncDatabase = Depends(get_db)
):
    """Login to get API Key"""
    try:
        user_collection = db[MONGODB_USERS_COLLECTION]

        user = await user_collection.find_one({"email": user_data.username})
        if (not user) or (not pl_ctx.verify(user_data.password, user["password"])):
            raise HTTPException(401, detail="Invalid email or password")
        
        return {
            "access_token": create_access_token(user_id=str(user["_id"]))
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error: {repr(exc)}")
        raise HTTPException(500, detail=str(exc))
    
@router.post(
    "/generate-api-key",
    tags=["auth"], response_model=GenerateApiKey
)
@auth_limiter.limit(AUTH_RATE_LIMIT)
async def generate_api_key(
    request: Request,
    user: dict = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db)
):
    """
    Generate an API Key.
    All keys generated prior to this one will be invalidated.
    """
    try:
        key_collection = db[MONGODB_API_KEYS_COLLECTION]

        time_now = datetime.now(timezone.utc)
        key, key_hash = create_api_key()
        await key_collection.update_one(
            {"user_id": user["_id"]},
            {
                "$set": {
                    "key_hash": key_hash,
                    "updated_at": time_now
                },
                "$setOnInsert": {
                    "user_id": user["_id"],
                    "created_at": time_now
                }
            },
            upsert=True
        )

        return {"key": key}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error: {repr(exc)}")
        raise HTTPException(500, detail=str(exc))
