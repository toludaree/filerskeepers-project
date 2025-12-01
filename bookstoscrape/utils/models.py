from dataclasses import dataclass
from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional


class Book(BaseModel):
    bts_id: int
    name: str
    description: Optional[str]
    url: HttpUrl
    category: str
    upc: str
    price: float
    tax: float
    in_stock: bool
    stock_count: int
    review_count: int
    cover_image_url: HttpUrl
    rating: Literal[1, 2, 3, 4, 5]

@dataclass
class SchedulerContext:
    etag: Optional[str]

@dataclass
class PageSession:
    sid: int
    stype = "page"
    page_url: str
    first_page: bool = False
    retry_count: int = 0

@dataclass
class BookSession:
    sid: int
    stype = "book"
    book_url: str
    scheduler_context: Optional[SchedulerContext] = None
    retry_count: int = 0
