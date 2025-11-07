import asyncio
import math
from httpx import AsyncClient, RequestError

from . import settings
from .fetch import fetch_page, fetch_book
from .manager import BookSession, PageSession, Manager
from .utils import extract_id_from_book_url


async def bookstoscrape_crawler(
    worker_count=5,
    max_retry_count=3,
    env="dev"
):
    manager = Manager(env=env, max_retry_count=max_retry_count)
    await manager.queue.put(PageSession(
        sid=1,
        page_url=f"{settings.BASE_URL}/page-1.html",
        first_page=True
    ))

    for i in range(worker_count):
        task = asyncio.create_task(worker(f"w{i+1}", manager))
        manager.workers.append(task)
    
    await manager.queue.join()

    for w in manager.workers:
        w.cancel()
    worker_results = await asyncio.gather(*manager.workers, return_exceptions=True)
    for wid, result in enumerate(worker_results):
        if isinstance(result, Exception):
            manager.logger.info(f"[manager] ❌ Worker w{wid} ended with exception: {repr(result)}")

async def worker(wid: int, manager: Manager):
    while True:
        session = None
        try:
            session: PageSession | BookSession = await manager.queue.get()
            if not session.retry_count:
                message = "Start"
            else:
                message = f"Retry ({session.retry_count})"
            manager.logger.info(f"[{wid}][{session.stype}][{session.sid}] 👨‍🍳 {message}")

            async with AsyncClient(follow_redirects=True, proxy=settings.PROXY, timeout=settings.REQUEST_TIMEOUT) as client:
                try:
                    if isinstance(session, PageSession):
                        book_count, book_urls = await fetch_page(client, session.page_url)
                        if session.first_page:
                            page_count = math.ceil(book_count / len(book_urls))
                            for i in range(2, page_count+1):
                                await manager.queue.put(PageSession(
                                    sid=i,
                                    page_url=f"{settings.BASE_URL}/page-{i}.html"
                                ))
                        for url in book_urls:
                            await manager.queue.put(BookSession(
                                sid=extract_id_from_book_url(url),
                                book_url=url
                            ))
                    else:
                        book = await fetch_book(
                            client,
                            session.sid, session.book_url
                        )
                        manager.cleanup(book, session.sid)
                except RequestError as exc:
                    manager.logger.warning(f"[{wid}][{session.stype}][{session.sid}] ❌ {repr(exc)}")
                    if session.retry_count < manager.max_retry_count:
                        session.retry_count += 1
                        await manager.queue.put(session)
                        manager.logger.info(f"[{wid}][{session.stype}][{session.sid}] 🤞 Queued for retry")
                    else:
                        manager.logger.info(f"[manager][{session.stype}][{session.sid}] 😑 Retry limit reached")
                    continue
                
        except asyncio.CancelledError:
            manager.logger.info(f"[manager] 😎 Worker {wid} stopped")
            break
        except Exception as exc:
            sid = f"[{session.stype}][{session.sid}]" if session else ""
            manager.logger.exception(f"[{wid}]{sid} ❌ {repr(exc)}")
        finally:
            if session:
                manager.queue.task_done()
