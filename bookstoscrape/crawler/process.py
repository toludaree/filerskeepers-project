from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .models import Book


def process_page(page: bytes, page_url: str) -> list[str]:
    """
    Retrieve all the book urls on a given page.
    """
    soup = BeautifulSoup(page, "html.parser")
    books_tag = soup.find_all(name="article", class_="product_pod")
    books_url = [
        urljoin(page_url, tag.h3.a.attrs["href"])
        for tag in books_tag
    ]
    return books_url

def process_book(content: bytes, book_url: str) -> Book:
    """
    Process book page and return a Book pydantic model.
    """
    return Book(
        id=0,
        name="",
        description="",
        category="",
        price_including_tax=0.0,
        price_excluding_tax=0.0,
        in_stock=False,
        stock_count=0,
        review_count=0,
        cover_image_url="https://cover_image.com",
        rating=1
    )
