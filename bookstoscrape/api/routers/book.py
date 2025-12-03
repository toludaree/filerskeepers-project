from bson import ObjectId
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from pymongo.asynchronous.database import AsyncDatabase
from typing import Annotated, Optional

from ...settings import (
    API_RATE_LIMIT, MONGODB_BOOK_COLLECTION, MONGODB_CHANGELOG_COLLECTION,
)
from ...utils.api import api_limiter, get_db, logger, require_api_key
from ...utils.common import Book, Category, Rating
from ..models.book import (
    BooksOverview, Changelog, ChangelogEvent, SortBy, SortOrder,
)


router = APIRouter()

@router.get(
    "/books",
    tags=["book"], response_model=BooksOverview
)
@api_limiter.limit(API_RATE_LIMIT)
async def get_books(
    request: Request,
    categories: Annotated[list[Category], Query()] = [],
    min_price: Annotated[Optional[float], Query()] = None,
    max_price: Annotated[Optional[float], Query()] = None,
    ratings: Annotated[list[Rating], Query()] = [],
    sort_by: Annotated[SortBy, Query()] = "rating",
    sort_order: Annotated[SortOrder, Query()] = "desc",
    limit: Annotated[int, Query(gt=0, le=100)] = 20,
    offset: Annotated[int, Query()] = 0,
    user_id: ObjectId = Depends(require_api_key),
    db: AsyncDatabase = Depends(get_db)
):
    """
    Get all books.
        - Filter by: categories, min_price, max_price, and ratings
        - Sort by: rating, price, and review_count
        - Paginate via limit and offset.
    """
    try:
        book_collection = db[MONGODB_BOOK_COLLECTION]

        filters = {}
        if categories:
            filters["category"] = {"$in": categories}
        if min_price or max_price:
            filters["price"] = ({"$gte": min_price} if min_price else {}) | \
                               ({"$lte": max_price} if max_price else {})
        if ratings:
            filters["rating"] = {"$in": ratings}

        books = await book_collection.find(
            filter=filters,
            projection={
                "_id": 0,
                "bts_id": 1, "name": 1, "category": 1, "price": 1,
                "rating": 1, "review_count": 1
            },
            sort=[
                (sort_by, -1 if sort_order == "desc" else 1),
                ("bts_id", 1)
            ],
            skip=offset, limit=limit
        ).to_list()

        return {"books": books}
    except Exception as exc:
        logger.error(f"Unexpected error: {repr(exc)}")
        raise HTTPException(500, detail=str(exc))
    
@router.get(
    "/books/{book_id}",
    tags=["book"], response_model=Book
)
@api_limiter.limit(API_RATE_LIMIT)
async def get_book(
    request: Request,
    book_id: int,
    user_id: ObjectId = Depends(require_api_key),
    db: AsyncDatabase = Depends(get_db)
):
    """
    Given a book's ID, return full details about the book
    """
    try:
        book_collection = db[MONGODB_BOOK_COLLECTION]

        book = await book_collection.find_one(
            filter={"bts_id": book_id},
            projection={"_id": 0, "crawl_metadata": 0}
        )
        if not book:
            raise HTTPException(404, detail="Book not found")
        
        return book
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Unexpected error: {repr(exc)}")
        raise HTTPException(500, detail=str(exc))
    
@router.get(
    "/changes",
    tags=["book"], response_model=Changelog
)
@api_limiter.limit(API_RATE_LIMIT)
async def get_changes(
    request: Request,
    events: Annotated[list[ChangelogEvent], Query()] = [],
    start_date: Annotated[Optional[date], Query()] = None,
    end_date: Annotated[Optional[date], Query()] = None,
    user_id: ObjectId = Depends(require_api_key),
    db: AsyncDatabase = Depends(get_db)
):
    try:
        changelog_collection = db[MONGODB_CHANGELOG_COLLECTION]

        filters = {}
        if events:
            filters["event"] = {"$in": events}
        if start_date or end_date:
            filters["timestamp"] = {}
            if start_date:
                start_datetime = datetime.combine(start_date, datetime.min.time())
                start_datetime = start_datetime.replace(tzinfo=timezone.utc)
                filters["timestamp"]["$gte"] = start_datetime
            if end_date:
                end_datetime = datetime.combine(end_date, datetime.max.time())
                end_datetime = end_datetime.replace(tzinfo=timezone.utc)
                filters["timestamp"]["$lte"] = end_datetime

        changelog = await changelog_collection.find(
            filter=filters,
            projection={"_id": 0},
            sort=[("timestamp", -1), ("bts_id", 1)]
        ).to_list()
        for log in changelog:
            log["timestamp"] = log["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

        return {"changes": changelog}
    except Exception as exc:
        logger.error(f"Unexpected error: {repr(exc)}")
        raise HTTPException(500, detail=str(exc))
