from bson import ObjectId
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated, Optional

from ..settings import ASYNC_MONGODB_DB, MONGODB_BOOK_COLLECTION
from .models import (
    Category, Book, BooksOverview, Rating, SortBy, SortOrder, UserData,
    SignUpResponseSchema, LoginResponseSchema,
)
from .utils import pl_ctx, create_access_token, get_current_user, create_api_key, require_api_key


app = FastAPI()

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.post("/signup", response_model=SignUpResponseSchema)
async def signup(user_data: UserData):
    """
    Sign up to be able to use the API
    """
    user_collection = ASYNC_MONGODB_DB["users"]

    if await user_collection.find_one({"email": user_data.email}):
        raise HTTPException(400, "User already exists")
    
    await user_collection.insert_one({
        "email": user_data.email,
        "password": pl_ctx.hash(user_data.password)
    })

    return {
        "message": "User created."
    }

@app.post("/login", response_model=LoginResponseSchema)
async def login(user_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login to get API key
    """
    user_collection = ASYNC_MONGODB_DB["users"]

    user = await user_collection.find_one({"email": user_data.username})
    print(user)
    if (not user) or (not pl_ctx.verify(user_data.password, user["password"])):
        raise HTTPException(401, "Invalid email or password")
    
    return {
        "access_token": create_access_token(user_id=str(user["_id"]))
    }

@app.get("/generate-api-key")
async def generate_api_key(user: dict = Depends(get_current_user)):
    """
    Generate an API key. All APIs generated prior to this one will be invalidated
    """
    key_collection = ASYNC_MONGODB_DB["api_keys"]
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
    return {
        "key": key
    }

@app.get("/books", response_model=BooksOverview)
async def get_books(
    categories: Annotated[list[Category], Query()] = [],
    min_price: Annotated[Optional[float], Query()] = None,
    max_price: Annotated[Optional[float], Query()] = None,
    ratings: Annotated[list[Rating], Query()] = [],
    sort_by: Annotated[SortBy, Query()] = "rating",
    sort_order: Annotated[SortOrder, Query()] = "desc",
    limit: Annotated[int, Query(gt=0, le=100)] = 20,
    offset: Annotated[int, Query()] = 0,
    user_id: ObjectId = Depends(require_api_key),
):
    """
    Get all books.

    Filter by:
        - category
        - minimum price
        - maximum price
        - rating

    Sort by:
        - rating
        - price
        - review count

    Paginate using limit and offset.
    """
    book_collection = ASYNC_MONGODB_DB[MONGODB_BOOK_COLLECTION]

    filters = {}
    if categories:
        filters["category"] = {"$in": categories}
    if any((min_price, max_price)):
        filters["price_excluding_tax"] = ({"$gte": min_price} if min_price else {}) | ({"$lte": max_price} if max_price else {})
    if ratings:
        filters["rating"] = {"$in": ratings}

    # print(f"Categories: {categories}")
    # print(f"Minimum Price: {min_price}")
    # print(f"Maximum Price: {max_price}")
    # print(f"Ratings: {ratings}")
    # print(filters)
    books = await book_collection.find(
        filter=filters,
        projection={
            "_id": 0,
            "bts_id": 1,
            "name": 1,
            "category": 1,
            "price_excluding_tax": 1,
            "rating": 1,
            "review_count": 1
        },
        sort=[
            ("price_excluding_tax" if sort_by == "price" else sort_by, -1 if sort_order == "desc" else 1),
            ("bts_id", 1)
        ],
        skip=offset,
        limit=limit,
    ).to_list()

    return {
        "books": books
    }

@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int, user_id: ObjectId = Depends(require_api_key)):
    """
    Given a book ID, return full details about the book
    """
    book_collection = ASYNC_MONGODB_DB[MONGODB_BOOK_COLLECTION]

    book: Optional[dict] = await book_collection.find_one(
        filter={"bts_id": book_id},
        projection={
            "_id": 0
        }
    )
    crawl_metadata = book.pop("crawl_metadata")
    book["source_url"] = crawl_metadata["source_url"]
    return book
