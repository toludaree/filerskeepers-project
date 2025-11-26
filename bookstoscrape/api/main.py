from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from typing import Annotated, Optional

from ..settings import ASYNC_MONGODB_DB, MONGODB_BOOK_COLLECTION
from .models import Category, Book, BooksOverview, Rating, SortBy, SortOrder

app = FastAPI()

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/books", response_model=BooksOverview)
async def get_books(
    categories: Annotated[list[Category], Query()] = [],
    min_price: Annotated[Optional[float], Query()] = None,
    max_price: Annotated[Optional[float], Query()] = None,
    ratings: Annotated[list[Rating], Query()] = [],
    sort_by: Annotated[SortBy, Query()] = "rating",
    sort_order: Annotated[SortOrder, Query()] = "desc",
    limit: Annotated[int, Query(gt=0, le=100)] = 20,
    offset: Annotated[int, Query()] = 0
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
async def get_book(book_id: int):
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
