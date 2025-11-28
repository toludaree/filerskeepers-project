from __future__ import annotations
from enum import IntEnum
from typing import Literal
from pydantic import BaseModel, EmailStr


class BooksOverview(BaseModel):
    books: list[BookOverview]

class BookOverview(BaseModel):
    bts_id: int
    name: str
    category: str
    price_excluding_tax: float
    rating: int
    review_count: float

class Book(BaseModel):
    bts_id: int
    name: str
    description: str
    source_url: str
    category: str
    price_excluding_tax: float
    in_stock: bool
    stock_count: int
    rating: int
    review_count: int
    cover_image_url: str

Category = Literal[
    "Travel", "Mystery", "Historical Fiction", "Sequential Art", "Classics",
    "Philosophy", "Romance", "Women's Fiction", "Fiction", "Childrens",
    "Religion", "Nonfiction", "Music", "Default", "Science Fiction",
    "Sports and Games", "Add a comment", "Fantasy", "New Adult",
    "Young Adult", "Science", "Poetry", "Paranormal", "Art", "Psychology",
    "Autobiography", "Parenting", "Adult Fiction", "Humor", "Horror",
    "History", "Food and Drink", "Christian Fiction", "Business", "Biography",
    "Thriller", "Contemporary", "Spirituality", "Academic", "Self Help",
    "Historical", "Christian", "Suspense", "Short Stories", "Novels",
    "Health", "Politics", "Cultural", "Erotica", "Crime",
]
class Rating(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
SortBy = Literal["rating", "price", "review_count"]
SortOrder = Literal["asc", "desc"]

class UserData(BaseModel):
    email: EmailStr
    password: str

class SignUpResponseSchema(BaseModel):
    message: str

class LoginResponseSchema(BaseModel):
    access_token: str
