from __future__ import annotations
from pydantic import BaseModel
from typing import Literal

from ...utils.common import Category, Rating


class BooksOverview(BaseModel):
    books: list[BookOverview]

class BookOverview(BaseModel):
    bts_id: int
    name: str
    category: Category
    price: float
    rating: Rating
    review_count: float

SortBy = Literal["rating", "price", "review_count"]
SortOrder = Literal["asc", "desc"]
