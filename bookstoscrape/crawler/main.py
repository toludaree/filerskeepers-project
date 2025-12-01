import asyncio
import logging
from dataclasses import asdict
from pymongo import IndexModel

from ..settings import BASE_URL
from ..utils.manager import Manager
from ..utils.models import Session


logging.basicConfig(level=logging.INFO)

async def bookstoscrape_crawler(
    worker_count=5,
    max_retry_count=3,
    env="dev",
    restart: bool = True
):
    logger = logging.getLogger(__name__)
    manager = Manager(env=env, logger=logger, max_retry_count=max_retry_count)
    
    crawler_state_collection = manager.mongodb_client["bookstoscrape"]["crawler_state"]
    if restart:
        await manager.drop_collections()
    
        indexes = await manager.book_collection.create_indexes(
            indexes=[
                IndexModel([("bts_id", 1)], unique=True),
                IndexModel([("category", 1), ("price", 1), ("rating", 1), ("review_count", 1)]),
                IndexModel([("category", 1), ("rating", 1), ("price", 1), ("review_count", 1)]),
                IndexModel([("price", 1), ("rating", 1), ("review_count", 1)]),
                IndexModel([("rating", 1), ("price", 1), ("review_count", 1)])
            ]
        )
        manager.logger.info(f"Indexes: {indexes}")

        first_page_session = Session(
            sid="p1",
            resource_id=1,
            resource_type="page",
            resource_url=f"{BASE_URL}/page-1.html",
        )
        await manager.queue.put(first_page_session)
        manager.run_state[first_page_session.sid] = asdict(first_page_session)
    else:
        async for doc in crawler_state_collection.find({}, {"_id": 0}):
            await manager.queue.put(Session(**doc))
            manager.run_state[doc["sid"]] = doc

    for i in range(worker_count):
        task = asyncio.create_task(manager.worker(f"w{i+1}"))
        manager.workers.append(task)
    
    # await manager.queue.join()
    worker_results = await asyncio.gather(*manager.workers, return_exceptions=True)
    for wid, result in enumerate(worker_results):
        if isinstance(result, Exception):
            manager.logger.info(f"[manager] ❌ Worker w{wid} ended with exception: {repr(result)}")

    await crawler_state_collection.drop()
    if manager.run_state:
        await crawler_state_collection.insert_many(manager.run_state.values())
    await manager.mongodb_client.close()
    # await manager.cancel_workers()
