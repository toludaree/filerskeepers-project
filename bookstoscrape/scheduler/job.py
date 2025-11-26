import asyncio
import logging
from typing import Literal

from ..settings import BASE_URL
from ..utils.manager import Manager
from ..utils.models import PageSession


logging.basicConfig(level=logging.INFO)

async def bts_scheduler(
    worker_count: int = 5,
    max_retry_count: int = 3,
    env: Literal["dev", "prod"] = "dev"
):
    logger = logging.getLogger(__name__)
    manager = Manager(env=env, logger=logger, crawler=False, max_retry_count=max_retry_count)
    await manager.get_current_books()
    await manager.queue.put(PageSession(
        sid=1,
        page_url=f"{BASE_URL}/page-1.html",
        first_page=True
    ))

    for i in range(worker_count):
        task = asyncio.create_task(manager.worker(f"w{i+1}"))
        manager.workers.append(task)
    
    await manager.queue.join()
    await manager.mongodb_client.close()
    await manager.cancel_workers()
