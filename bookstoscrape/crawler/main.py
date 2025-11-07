import asyncio
import logging
import math
from httpx import AsyncClient

from .fetch import fetch_page, fetch_book
from .manager import BookSession, PageSession, Manager
from .utils import extract_id_from_book_url


async def bookstoscrape_crawler(
    max_workers=5,
    env="dev"
):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    manager = Manager(logger=logger, env=env)

    async with AsyncClient() as client:
        book_count, first_page_urls = await fetch_page(
            client,
            page_url="https://books.toscrape.com/catalogue/page-1.html"
        )
    page_count = math.ceil(book_count / len(first_page_urls))
    for i in range(2, page_count+1):
        await manager.queue.put(PageSession(
            sid=i, page_num=i,
            page_url=f"https://books.toscrape.com/catalogue/page-{i}.html"
        ))
    for url in first_page_urls:
        await manager.queue.put(BookSession(
            sid=extract_id_from_book_url(url),
            book_url=url
        ))

    for i in range(max_workers):
        task = asyncio.create_task(worker(f"w{i+1}", manager))
        manager.workers.append(task)
    
    await manager.queue.join()

    for w in manager.workers:
        w.cancel()
    worker_results = await asyncio.gather(*manager.workers, return_exceptions=True)
    for wid, result in enumerate(worker_results):
        if isinstance(result, Exception):
            logger.info(f"[manager] ❌ Worker w{wid} ended with exception: {repr(result)}")

async def worker(wid: int, manager: Manager):
    while True:
        try:
            session: PageSession | BookSession = await manager.queue.get()
            if not session.retry_count:
                message = "Start"
            else:
                message = f"Retry ({session.retry_count})"

            async with AsyncClient() as client:
                if isinstance(session, PageSession):
                    _, book_urls = await fetch_page(client, session.page_url)
                    for url in book_urls:
                        await manager.queue.put(BookSession(
                            sid=extract_id_from_book_url(url),
                            book_url=url
                        ))
                else:
                    book = await fetch_book(client, session.book_url)

        except:
            ...
