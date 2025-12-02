import asyncio
from dataclasses import asdict
from typing import Literal

from .. import settings as ss
from ..crawler.manager import Manager
from ..crawler.models import Session
from ..utils.common import setup_logging


async def bts_scheduler(
    env: Literal["dev", "prod"] = "dev"
):
    logger = setup_logging("scheduler")
    manager = Manager(env, logger, is_scheduler=True)
    
    # Retrieve stored books from collection
    async for book in manager.book_collection.find({}, ss.CHANGE_DETECTION_FIELDS):
        manager.stored_books[book["bts_id"]] = book

    first_page_session = Session(
        sid="p1",
        resource_id=1,
        resource_type="page",
        resource_url=f"{ss.BASE_URL}/page-1.html"
    )
    await manager.queue.put(first_page_session)
    manager.crawler_state[first_page_session.sid] = asdict(first_page_session)

    for i in range(ss.WORKER_COUNT):
        task = asyncio.create_task(manager.worker(f"w{i+1}"))
        manager.workers.append(task)

    await asyncio.gather(*manager.workers, return_exceptions=True)

    await manager.close_db_client()
