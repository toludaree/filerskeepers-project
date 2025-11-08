import asyncio
from httpx import AsyncClient

from .models import Book
from .process import process_page, process_book
from .settings import BROWSER_HEADERS


async def fetch_page(
    client: AsyncClient,
    page_url: str
) -> tuple[int, list[str]]:
    page = await client.get(
        url=page_url,
        headers=BROWSER_HEADERS
    )
    page.raise_for_status()
    
    book_count, urls = await asyncio.to_thread(
        process_page, page.content, page_url
    )
    return book_count, urls

async def fetch_book(client: AsyncClient, book_url: str) -> Book:
    book_page = await client.get(
        url=book_url,
        headers=BROWSER_HEADERS
    )
    book_page.raise_for_status()

    book = await asyncio.to_thread(
        process_book, book_page, book_url
    )
    return book
