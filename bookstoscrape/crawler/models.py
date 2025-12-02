from dataclasses import dataclass
from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional


@dataclass
class Session:
    sid: str  # session id
    resource_id: int
    resource_type: Literal["page", "book"]
    resource_url: str
    retry_count: int = 0

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
