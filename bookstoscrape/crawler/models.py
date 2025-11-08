from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional


class Book(BaseModel):
    _id: int
    name: str
    description: Optional[str]
    category: str
    price_including_tax: float
    price_excluding_tax: float
    in_stock: bool
    stock_count: int
    review_count: int
    cover_image_url: HttpUrl
    rating: Literal[1, 2, 3, 4, 5]
