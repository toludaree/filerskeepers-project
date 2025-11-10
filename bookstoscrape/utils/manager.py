import asyncio
import math
from httpx import AsyncClient, HTTPError
from logging import Logger
from pymongo import AsyncMongoClient
from typing import Literal, Optional

from .common import extract_id_from_book_url, get_milliseconds_since_epoch
from .exceptions import ProcessingError
from .fetch import fetch_page, fetch_book
from .models import PageSession, Book, BookSession, SchedulerContext
from ..settings import (
    BASE_URL, CHANGE_DETECTION_FIELDS, MONGODB_CONNECTION_URI, MONGODB_DB,
    MONGODB_BOOK_COLLECTION, MONGODB_CHANGELOG_COLLECTION, PROXY,
    REQUEST_TIMEOUT,
)


class Manager:
    def __init__(self, env: Literal["dev", "prod"], logger: Logger, crawler: bool, max_retry_count: int):
        self.queue = asyncio.Queue()
        self.workers: list[asyncio.Task] = []
        self.logger = logger

        self.env = env
        self.crawler = crawler
        self.max_retry_count = max_retry_count

        self.mongodb_client = AsyncMongoClient(MONGODB_CONNECTION_URI, timeoutMS=5000)
        self.db = self.mongodb_client[MONGODB_DB]
        self.book_collection = self.db[MONGODB_BOOK_COLLECTION]
        self.changelog_collection = self.db[MONGODB_CHANGELOG_COLLECTION]
        self.current_books = {}

    async def drop_collections(self):
        collection_names = await self.db.list_collection_names()
        if MONGODB_BOOK_COLLECTION in collection_names:
            await self.book_collection.drop()
            self.logger.info(f"[manager] Dropped collection: {MONGODB_BOOK_COLLECTION}")
        if MONGODB_CHANGELOG_COLLECTION in collection_names:
            await self.changelog_collection.drop()
            self.logger.info(f"[manager] Dropped collection: {MONGODB_CHANGELOG_COLLECTION}")
    
    async def get_current_books(self):
        async for book in self.book_collection.find({}, CHANGE_DETECTION_FIELDS):
            self.current_books[book["bts_id"]] = book

    async def worker(self, wid: int):
        while True:
            session = None
            try:
                session: PageSession | BookSession = await self.queue.get()
                log_id = f"[{wid}][{session.stype}][{session.sid}]"
                initial_message = self._get_initial_worker_message(session.retry_count)
                self.logger.info(f"{log_id} {initial_message}")

                async with AsyncClient(
                    follow_redirects=True,
                    proxy=PROXY,
                    timeout=REQUEST_TIMEOUT
                ) as client:
                    try:
                        if isinstance(session, PageSession):
                            book_count, book_urls = await fetch_page(client, session.page_url)

                            if self.env == "prod":
                                if session.first_page:
                                    page_count = math.ceil(book_count / len(book_urls))
                                    for i in range(2, page_count+1):
                                        await self.queue.put(PageSession(
                                            sid=i,
                                            page_url=f"{BASE_URL}/page-{i}.html"
                                        ))

                            for url in book_urls:
                                book_id = extract_id_from_book_url(url)
                                if self.crawler:
                                    scheduler_context = None
                                else:
                                    stored_book = self.current_books.get(book_id)
                                    scheduler_context = SchedulerContext(
                                        etag=stored_book["crawl_metadata"]["etag"] if stored_book else None
                                    )
                                await self.queue.put(BookSession(
                                    sid=book_id,
                                    book_url=url,
                                    scheduler_context=scheduler_context,
                                ))
                        else:
                            etag, book = await fetch_book(client, session)
                            await self._push_to_storage(session, etag, book)
                    except HTTPError as exc:
                        self.logger.warning(f"[{log_id}] ❌ {repr(exc)}")
                        if session.retry_count < self.max_retry_count:
                            session.retry_count += 1
                            await self.queue.put(session)
                            self.logger.info(f"[{log_id}] 🤞 Queued for retry")
                        else:
                            self.logger.warning(f"[{log_id}] Retry limit reached")
                            if isinstance(session, BookSession) and self.crawler:
                                await self._push_to_storage(session, None, None)
                        continue
                    except ProcessingError:
                        self.logger.exception(f"[{log_id}] ❌ {repr(exc)}")
                        ... # send email
            except asyncio.CancelledError:
                self.logger.info(f"Worker {wid} stopped")
                raise
            except Exception as exc:
                self.logger.exception(f"[{wid}] ❌ {repr(exc)}")
            finally:
                if session:
                    self.queue.task_done()

    def _get_initial_worker_message(self, retry_count: int):
        if not retry_count:
            return "Start"
        else:
            return f"Retry {retry_count}"

    async def _push_to_storage(self, session: BookSession, etag: Optional[str], book: Optional[Book]):
        if (not self.crawler) and (not book):  # Scheduler with no result
            self.logger.info(f"[manager] Unchanged: {session.sid}")
            return
        
        timestamp = get_milliseconds_since_epoch()
        document = book.model_dump(mode="json") if book else {}
        document["crawl_metadata"] = {
            "timestamp": timestamp,
            "status": "success" if book else "failed",
            "source_url": session.book_url,
            "etag": etag
        }

        if self.crawler:
            await self.book_collection.insert_one(document)
            self.logger.info(f"[manager] Pushed to storage: {session.sid}")
        else:
            update_record = await self.book_collection.replace_one(
                filter={"crawl_metadata.source_url": session.book_url},
                replacement=document,
                upsert=True
            )
            if update_record.did_upsert:
                self.logger.info(f"[manager] Book created: {session.sid}")
                event = "create"
                changes = {}
            else:
                self.logger.info(f"[manager] Book updated: {session.sid}")
                event = "update"
                changes = self.get_update_changes(book.model_dump(mode="json"))
            await self.changelog_collection.insert_one({
                "bts_id": session.sid,
                "event": event,
                "timestamp": timestamp,
                "changes": changes
            })

    def get_update_changes(self, book: dict):
        changes = {}
        old_version: dict = self.current_books[book["bts_id"]]

        for k in old_version.keys():
            if k  in ("bts_id", "crawl_metadata"):
                continue
            if (old:=old_version[k]) != (new:=book[k]):
                changes[k] = {"old": old, "new": new}
        
        return changes

    async def cancel_workers(self):
        for w in self.workers:
            w.cancel()
        worker_results = await asyncio.gather(*self.workers, return_exceptions=True)
        for wid, result in enumerate(worker_results):
            if isinstance(result, Exception):
                self.logger.info(f"[manager] ❌ Worker w{wid} ended with exception: {repr(result)}")
