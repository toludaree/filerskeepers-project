import re
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
    rating_dict = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    soup = BeautifulSoup(content, "html.parser")
    book_tag = soup.find(name="article", class_="product_page")
    info_table = book_tag.table

    book_id = re.search(r"_(\d+)/index\.html$", book_url).group(1)
    book_name = book_tag.h1.text.strip()
    book_description = book_tag.find(name="div", id="product_description") \
                               .find_next_sibling(name="p").text.strip()
    book_category = soup.find(name="ul", class_="breadcrumb") \
                        .find_all(name="li")[2].text.strip()
    book_price_incl_tax = float(info_table.find("th", string="Price (incl. tax)").parent.td.text.replace("£", ""))
    book_price_excl_tax = float(info_table.find("th", string="Price (excl. tax)").parent.td.text.replace("£", ""))
    availability: str = info_table.find("th", string="Availability").parent.td.text
    if availability.startswith("In stock"):
        in_stock = True
        stock_count = int(availability.split("In stock")[-1].strip().split()[0][1:])
    else:
        in_stock = False
        stock_count = 0
    review_count = int(info_table.find("th", string="Number of reviews").parent.td.text)
    cover_image_url = urljoin(book_url, book_tag.find("div", id="product_gallery").find("img").attrs["src"])
    book_rating = rating_dict[book_tag.find("p", class_="star-rating").attrs["class"][-1]]

    return Book(
        id=book_id,
        name=book_name,
        description=book_description,
        category=book_category,
        price_including_tax=book_price_incl_tax,
        price_excluding_tax=book_price_excl_tax,
        in_stock=in_stock,
        stock_count=stock_count,
        review_count=review_count,
        cover_image_url=cover_image_url,
        rating=book_rating
    )
