import asyncio
import math
from dataclasses import asdict
from datetime import datetime, timezone
from httpx import AsyncClient, HTTPError
from logging import Logger
from pathlib import Path
from pymongo import AsyncMongoClient
from typing import Literal, Optional

from .common import extract_id_from_book_url, get_milliseconds_since_epoch
from .exceptions import ProcessingError
from .fetch import fetch_page, fetch_book
from .models import Book, Session
from ..settings import (
    BASE_URL, CHANGE_DETECTION_FIELDS, MONGODB_CONNECTION_URI, MONGODB_DB,
    MONGODB_BOOK_COLLECTION, MONGODB_CHANGELOG_COLLECTION, PROXY,
    REQUEST_TIMEOUT,
)


class Manager:
    def __init__(self, env: Literal["dev", "prod"], logger: Logger, max_retry_count: int, is_scheduler: bool = False):
        self.queue = asyncio.Queue()
        self.workers: list[asyncio.Task] = []
        self.logger = logger

        self.env = env
        self.is_scheduler = is_scheduler
        self.max_retry_count = max_retry_count

        self.run_state = {}

        if self.is_scheduler:
            self.snapshot_folder = Path(f"bookstoscrape/snapshots/scheduler/{str(datetime.now().date()).replace("-", "")}")
        else:
            self.snapshot_folder = Path("bookstoscrape/snapshots/crawler")
        self.snapshot_folder.mkdir(parents=True, exist_ok=True)

        self.shutdown_event = asyncio.Event()
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5
        self.failure_lock = asyncio.Lock()

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
        while not self.shutdown_event.is_set():
            session = None
            try:
                try:
                    session: Session = await asyncio.wait_for(self.queue.get(), 10)
                except asyncio.TimeoutError:
                    if not self.shutdown_event.is_set():
                        self.logger.info("No new queue entry for 10 seconds. Run complete")
                        self.shutdown_event.set()
                    continue

                log_id = f"[{wid}][{session.resource_type}][{session.sid}]"
                initial_message = self._get_initial_worker_message(session.retry_count)
                self.logger.info(f"{log_id} {initial_message}")

                async with AsyncClient(
                    follow_redirects=True,
                    proxy=PROXY,
                    timeout=REQUEST_TIMEOUT
                ) as client:
                    try:
                        if session.resource_type == "page":
                            book_count, book_urls = await fetch_page(client, session.resource_url)

                            if self.env == "prod":
                                if session.resource_id == 1:
                                    page_count = math.ceil(book_count / len(book_urls))
                                    for i in range(2, page_count+1):
                                        page_session = Session(
                                            sid=f"p{i}",
                                            resource_id=i,
                                            resource_type="page",
                                            resource_url=f"{BASE_URL}/page-{i}.html"
                                        )
                                        await self.queue.put(page_session)
                                        self.run_state[page_session.sid] = asdict(page_session)

                            for url in book_urls:
                                book_id = extract_id_from_book_url(url)
                                book_session = Session(
                                    sid=f"b{book_id}",
                                    resource_id=book_id,
                                    resource_type="book",
                                    resource_url=url,
                                )
                                await self.queue.put(book_session)
                                self.run_state[book_session.sid] = asdict(book_session)
                        else:
                            if self.is_scheduler:
                                stored_book = self.current_books.get(session.resource_id)
                                last_etag = stored_book["crawl_metadata"]["etag"]
                            else:
                                last_etag = None
                            etag, book = await fetch_book(client, session.resource_id, session.resource_url, last_etag, self.snapshot_folder)
                            await self._push_to_storage(session, etag, book)

                        self.run_state.pop(session.sid)
                        await self.track_run_status(True)
                    except HTTPError as exc:
                        self.logger.warning(f"[{log_id}] ❌ {repr(exc)}")
                        if session.retry_count < self.max_retry_count:
                            session.retry_count += 1
                            await self.queue.put(session)
                            self.logger.info(f"[{log_id}] 🤞 Queued for retry")
                        else:
                            self.logger.warning(f"[{log_id}] Retry limit reached")
                            if (session.resource_type == "book") and (not self.is_scheduler):
                                await self._push_to_storage(session, None, None)
                        await self.track_run_status(False)
                        continue
                    except ProcessingError as exc:
                        self.logger.exception(f"[{log_id}] ❌ {repr(exc)}")
                        await self.track_run_status(False)
                        ... # send email
            except asyncio.CancelledError:
                self.logger.info(f"Worker {wid} stopped")
                raise
            except Exception as exc:
                self.logger.exception(f"[{wid}] ❌ {repr(exc)}")
                await self.track_run_status(False)
            finally:
                if session:
                    self.queue.task_done()
        else:
            self.logger.info(f"Worker {wid} stopped")

    def _get_initial_worker_message(self, retry_count: int):
        if not retry_count:
            return "Start"
        else:
            return f"Retry {retry_count}"

    async def track_run_status(self, success: bool = True):
        async with self.failure_lock:
            if not self.shutdown_event.is_set():
                if success:
                    self.consecutive_failures = 0
                else:
                    self.consecutive_failures += 1
                
                if self.consecutive_failures > self.max_consecutive_failures:
                    self.logger.info("Maximum failure reached. Setting shutdown event")
                    self.shutdown_event.set()

    async def _push_to_storage(self, session: Session, etag: Optional[str], book: Optional[Book]):
        if self.is_scheduler and (not book):  # Scheduler with no result
            self.logger.info(f"[manager] Unchanged: {session.sid}")
            return
        
        timestamp = get_milliseconds_since_epoch()
        document = book.model_dump(mode="json") if book else {}
        document["crawl_metadata"] = {
            "timestamp": datetime.now(timezone.utc),
            "status": "success" if book else "failed",
            "source_url": session.resource_url,
            "etag": etag or ""   # ensure that it is not None
        }

        if not self.is_scheduler:
            await self.book_collection.insert_one(document)
            self.logger.info(f"[manager] Pushed to storage: {session.sid}")
        else:
            update_record = await self.book_collection.replace_one(
                filter={"crawl_metadata.source_url": session.resource_url},
                replacement=document,
                upsert=True
            )
            if update_record.did_upsert:
                self.logger.info(f"[manager] Book added: {session.sid}")
                event = "add"
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
            if k in ("bts_id", "crawl_metadata"):
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
