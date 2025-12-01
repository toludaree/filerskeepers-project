import asyncio
import logging
from dataclasses import asdict

from ..settings import BASE_URL
from ..utils.manager import Manager
from ..utils.models import Session


logging.basicConfig(level=logging.INFO)

async def bookstoscrape_crawler(
    worker_count=5,
    max_retry_count=3,
    env="dev"
):
    logger = logging.getLogger(__name__)
    manager = Manager(env=env, logger=logger, max_retry_count=max_retry_count)
    await manager.drop_collections()

    first_page_session = Session(
        sid="p1",
        resource_id=1,
        resource_type="page",
        resource_url=f"{BASE_URL}/page-1.html",
    )
    await manager.queue.put(first_page_session)
    manager.run_state[first_page_session.sid] = asdict(first_page_session)

    for i in range(worker_count):
        task = asyncio.create_task(manager.worker(f"w{i+1}"))
        manager.workers.append(task)
    
    # await manager.queue.join()
    worker_results = await asyncio.gather(*manager.workers, return_exceptions=True)
    for wid, result in enumerate(worker_results):
        if isinstance(result, Exception):
            manager.logger.info(f"[manager] ❌ Worker w{wid} ended with exception: {repr(result)}")

    crawler_state_collection = manager.mongodb_client["bookstoscrape"]["crawler_state"]
    await crawler_state_collection.drop()
    if manager.run_state:
        await crawler_state_collection.insert_many(manager.run_state.values())
    await manager.mongodb_client.close()
    # await manager.cancel_workers()
