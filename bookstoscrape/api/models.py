from __future__ import annotations
from pydantic import BaseModel


class GetBooksResponseModel(BaseModel):
    books: list[BookOverview]

class BookOverview(BaseModel):
    bts_id: int
    name: str
    category: str
    price: float
    rating: float
    reviews: float

class BookFull(BaseModel):
    bts_id: int
    name: str
    description: str
    source_url: str
    category: str
    price: float
    in_stock: bool
    stock_count: int
    rating: float
    review_count: int
    cover_image_url: str
