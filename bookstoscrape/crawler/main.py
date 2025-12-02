import asyncio
from dataclasses import asdict
from pymongo import IndexModel
from typing import Literal

from ..settings import BASE_URL, WORKER_COUNT
from ..utils.common import setup_logging
from ..utils.crawler import build_cli_parser
from .manager import Manager
from .models import Session


async def bts_crawler(
    env: Literal["dev", "prod"] ="dev",
    restart: bool = True
):
    logger = setup_logging(run_type="crawler")
    manager = Manager(env, logger)
    
    if restart:
        await manager.book_collection.drop()
        await manager.changelog_collection.drop()
        manager.logger.info("[manager] Dropped book and changelog collections")

        # Clean snapshot folder
        for item in manager.snapshot_folder.iterdir():
            if item.is_file:
                item.unlink()
    
        indexes = await manager.book_collection.create_indexes(
            indexes=[
                IndexModel([("bts_id", 1)], unique=True),
                IndexModel([("category", 1), ("price", 1), ("rating", 1), ("review_count", 1)]),
                IndexModel([("category", 1), ("rating", 1), ("price", 1), ("review_count", 1)]),
                IndexModel([("price", 1), ("rating", 1), ("review_count", 1)]),
                IndexModel([("rating", 1), ("price", 1), ("review_count", 1)])
            ]
        )
        manager.logger.info(f"[manager] Indexes created: {indexes}")

        first_page_session = Session(
            sid="p1",
            resource_id=1,
            resource_type="page",
            resource_url=f"{BASE_URL}/page-1.html",
        )
        await manager.queue.put(first_page_session)
        manager.crawler_state[first_page_session.sid] = asdict(first_page_session)
    else:
        async for doc in manager.crawler_state_collection.find({}, {"_id": 0}):
            await manager.queue.put(Session(**doc))
            manager.crawler_state[doc["sid"]] = doc

    for i in range(WORKER_COUNT):
        task = asyncio.create_task(manager.worker(f"w{i+1}"))
        manager.workers.append(task)

    await asyncio.gather(*manager.workers, return_exceptions=True)

    await manager.crawler_state_collection.drop()
    if manager.crawler_state:
        await manager.crawler_state_collection.insert_many(manager.crawler_state.values())
    await manager.close_db_client()

def cli():
    parser = build_cli_parser()
    args = parser.parse_args()
    asyncio.run(bts_crawler(env=args.env, restart=args.restart))


if __name__ == "__main__":
    cli()
