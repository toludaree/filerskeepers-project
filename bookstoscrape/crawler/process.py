from bs4 import BeautifulSoup
from urllib.parse import urljoin


def process_page(page: bytes, page_url: str):
    """
    Retrieve all the book urls on a given page
    """
    soup = BeautifulSoup(page, "html.parser")
    books_tag = soup.find_all(name="article", class_="product_pod")
    books_url = [
        urljoin(page_url, tag.h3.a.attrs["href"])
        for tag in books_tag
    ]
    return books_url
