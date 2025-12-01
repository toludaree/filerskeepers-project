import asyncio
from httpx import AsyncClient
from typing import Optional

from .models import Book, BookSession
from .process import process_page, process_book
from ..settings import BROWSER_HEADERS


async def fetch_page(
    client: AsyncClient,
    page_url: str,
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

async def fetch_book(
    client: AsyncClient,
    book_id: int,
    book_url: str,
    last_etag: Optional[str]
):
    if etag is not None:
        headers = BROWSER_HEADERS | {
            "if-none-match": last_etag
        }
    else:
        headers = BROWSER_HEADERS
    
    book_page = await client.get(
        url=book_url,
        headers=headers
    )

    etag = book_page.headers["etag"]
    if book_page.status_code == 304:
        return etag, None
    
    book_page.raise_for_status()

    book = await asyncio.to_thread(
        process_book, book_page.content, book_id, book_url
    )
    return etag, book
