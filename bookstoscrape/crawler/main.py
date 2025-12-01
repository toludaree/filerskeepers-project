import asyncio
import logging

from ..settings import BASE_URL
from ..utils.manager import Manager
from ..utils.models import PageSession


logging.basicConfig(level=logging.INFO)

async def bookstoscrape_crawler(
    worker_count=5,
    max_retry_count=3,
    env="dev"
):
    logger = logging.getLogger(__name__)
    manager = Manager(env=env, logger=logger, max_retry_count=max_retry_count)
    await manager.drop_collections()
    await manager.queue.put(PageSession(
        sid="p1",
        page_id=1,
        page_url=f"{BASE_URL}/page-1.html",
    ))

    for i in range(worker_count):
        task = asyncio.create_task(manager.worker(f"w{i+1}"))
        manager.workers.append(task)
    
    # await manager.queue.join()
    worker_results = await asyncio.gather(*manager.workers, return_exceptions=True)
    for wid, result in enumerate(worker_results):
        if isinstance(result, Exception):
            manager.logger.info(f"[manager] ❌ Worker w{wid} ended with exception: {repr(result)}")
    await manager.mongodb_client.close()
    # await manager.cancel_workers()
