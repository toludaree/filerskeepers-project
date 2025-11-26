from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from ..settings import ASYNC_MONGODB_DB, MONGODB_BOOK_COLLECTION
from .models import GetBooksResponseModel

app = FastAPI()

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/books", response_model=GetBooksResponseModel)
async def get_books():
    """
    Get all books from the mongodb database

    Filter by:
        - category
    """
    book_collection = ASYNC_MONGODB_DB[MONGODB_BOOK_COLLECTION]

    books = await book_collection.find(
        {},
        { "_id": 0, "bts_id": 1, "name": 1, "cover_image_url": 1 }
    ).to_list()

    return {
        "books": books
    }
