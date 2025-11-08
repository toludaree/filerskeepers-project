import json
import logging
from asyncio import Queue, Task
from dataclasses import dataclass
from pathlib import Path
from pymongo import AsyncMongoClient
from typing import Literal, Optional

from .models import Book
from .settings import MONGODB_CONNECTION_URI, MONGODB_DB, MONGODB_COLLECTION
from .utils import get_milliseconds_since_epoch


@dataclass
class PageSession:
    sid: int
    stype = "page"
    page_url: str
    first_page: bool = False
    retry_count: int = 0

@dataclass
class BookSession:
    sid: int
    stype = "book"
    book_url: str
    result: Optional[Book] = None
    retry_count: int = 0

class Manager:
    def __init__(self, env: Literal["dev", "prod"], max_retry_count: int):
        self.queue = Queue()
        self.workers: list[Task] = []
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.env = env
        self.max_retry_count = max_retry_count
        
        self.mongodb_client = AsyncMongoClient(MONGODB_CONNECTION_URI, timeoutMS=5000)
        self.db = self.mongodb_client[MONGODB_DB]
        self.collection = self.db[MONGODB_COLLECTION]

    async def drop_collection_if_exists(self):
        collection_names = await self.db.list_collection_names()
        if MONGODB_COLLECTION in collection_names:
            await self.collection.drop()
            self.logger.info(f"[manager] Dropped collection: {MONGODB_COLLECTION}")

    async def cleanup(self, session: BookSession):
        crawl_timestamp = get_milliseconds_since_epoch()
        if session.result:
            metadata = {
                "timestamp": crawl_timestamp,
                "status": "success",
                "source_url": session.book_url
            }
            record = session.result.model_dump(mode="json")
            record["_id"] = session.sid
            record["crawl_metadata"] = metadata
            await self.collection.insert_one(record)
        else:
            metadata = {
                "timestamp": crawl_timestamp,
                "status": "failed",
                "source_url": session.book_url
            }
            record = {
                "_id": session.sid,
                "crawl_metadata": metadata
            }
            await self.collection.insert_one(record)
        self.logger.info(f"[manager] Pushed to mongo: {session.sid}")
        # if self.env == "dev":
        #     with open(self.storage_dev_path / f"{sid}.json", "w") as f:
        #         json.dump(result.model_dump(mode="json"), f)
        # self.logger.info(f"[manager] Ready: {sid}")
