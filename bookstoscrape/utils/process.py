import re
from bs4 import BeautifulSoup, Tag
from typing import Literal, Optional
from urllib.parse import urljoin

from .exceptions import ProcessingError
from .models import Book
from ..settings import BOOK_RATING_MAPPER


def process_page(page: bytes, page_url: str) -> tuple[int, list[str]]:
    """
    Extract the total number of books and all the book urls on a given page.
    """
    try:
        soup = BeautifulSoup(page, "html.parser")
        total_book_count = extract_total_book_count(soup)
        book_urls = extract_book_urls(soup, page_url)
        return total_book_count, book_urls
    except Exception as exc:
        raise ProcessingError("page") from exc

def extract_total_book_count(soup: BeautifulSoup) -> int:
    """Extract the total number of books"""
    book_count = soup.find("form", class_="form-horizontal") \
        .find(string=re.compile("results")) \
        .find_previous_sibling().text
    return int(book_count)

def extract_book_urls(soup: BeautifulSoup, page_url: str) -> list[str]:
    """Extract all the book URLs on a page"""
    article_tags = soup.find_all("article", class_="product_pod")
    return [
        urljoin(page_url, tag.h3.a.attrs["href"])
        for tag in article_tags
    ]

def process_book(content: bytes, book_id: int, book_url: str) -> Book:
    """
    Process book page and return a Book pydantic model.
    """
    try:
        soup = BeautifulSoup(content, "html.parser")
        article_tag = soup.find(name="article", class_="product_page")
        info_table = article_tag.table

        availability = extract_availability(info_table)
        if availability.startswith("In stock"):
            in_stock = True
            stock_count = re.search(r"(\d+)", availability).group()
        else:
            in_stock = False
            stock_count = 0
        
        return Book(
            bts_id=book_id,
            name=extract_book_name(article_tag),
            description=extract_book_description(article_tag),
            url=book_url,
            category=extract_book_category(soup),
            upc=extract_upc(soup),
            price=extract_price(info_table),
            tax=extract_tax(info_table),
            in_stock=in_stock,
            stock_count=stock_count,
            review_count=extract_review_count(info_table),
            cover_image_url=extract_cover_image(article_tag, book_url),
            rating=BOOK_RATING_MAPPER[extract_book_rating(article_tag)]
        )
    except Exception as exc:
        raise ProcessingError("book") from exc

def extract_book_name(article_tag: Tag) -> str:
    """Extract book name"""
    name: str = article_tag.h1.text
    return name.strip()

def extract_book_description(article_tag: Tag) -> Optional[str]:
    """Extract book description"""
    description_tag = article_tag.find("div", id="product_description")
    if description_tag:
        description: str = description_tag.find_next_sibling(name="p").text
        return description.strip()

def extract_book_category(soup: BeautifulSoup) -> str:
    """ Extract book category"""
    category: str = soup.find("ul", class_="breadcrumb") \
        .find_all("li")[2].text
    return category.strip()

def extract_upc(info_table: Tag) -> str:
    """Extract the Universal Product Code of the book"""
    return extract_td_given_th(info_table, "UPC")

def extract_price(info_table: Tag) -> float:
    """Extract price (excluding tax)"""
    th_text = extract_td_given_th(info_table, "Price (excl. tax)")
    return float(th_text.replace("£", ""))

def extract_tax(info_table: Tag) -> str:
    """Extract tax on book"""
    th_text = extract_td_given_th(info_table, "Tax")
    return float(th_text.replace("£", ""))

def extract_availability(info_table: Tag) -> str:
    """Extract stock availability"""
    return extract_td_given_th(info_table, "Availability")

def extract_review_count(info_table: Tag) -> int:
    """Extract review count"""
    return int(extract_td_given_th(info_table, "Number of reviews"))

def extract_cover_image(article_tag: Tag, book_url: str) -> str:
    """Extract book cover image"""
    relative_url = article_tag.find("div", id="product_gallery").find("img").attrs["src"]
    return urljoin(book_url, relative_url)

def extract_book_rating(article_tag: Tag) -> Literal["One", "Two", "Three", "Four", "Five"]:
    """Extract book rating"""
    return article_tag.find("p", class_="star-rating").attrs["class"][-1]

def extract_td_given_th(info_table: Tag, th_text: str) -> str:
    """Extract table data text given the table header text"""
    return info_table.find("th", string=th_text).parent.td.text
