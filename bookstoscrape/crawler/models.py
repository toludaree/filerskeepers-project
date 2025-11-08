from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional


class Book(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str    # Should I use a Literal type? What if the site changes? Doesn't seem worth it to break tbe run over a new category. Something like a simple warning will suffice.
    price_including_tax: float  # excluding should be first
    price_excluding_tax: float  # perhaps use a money type
    in_stock: bool
    stock_count: int
    review_count: int
    cover_image_url: HttpUrl
    rating: Literal[1, 2, 3, 4, 5]
