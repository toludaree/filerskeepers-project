import asyncio
import math
from dataclasses import asdict
from datetime import datetime, timezone
from httpx import AsyncClient, HTTPError
from logging import Logger
from pathlib import Path
from pymongo import AsyncMongoClient
from typing import Literal, Optional

from .. import settings as ss
from ..utils.crawler import extract_id_from_book_url
from .exceptions import ProcessingError
from .fetch import fetch_page, fetch_book
from .models import Book, Session


class Manager:
    def __init__(
        self,
        env: Literal["dev", "prod"], logger: Logger,
        max_retry_count: int, max_consecutive_failures: int,
        is_scheduler: bool = False
    ):
        self.queue = asyncio.Queue()
        self.workers: list[asyncio.Task] = []
        self.env = env
        self.logger = logger
        self.is_scheduler = is_scheduler
        self.max_retry_count = max_retry_count
        self.max_consecutive_failures = max_consecutive_failures
        self.consecutive_failures = 0
        self.run_status_lock = asyncio.Lock()
        self.shutdown_event = asyncio.Event()

        self._mongodb_client = AsyncMongoClient(ss.MONGODB_CONNECTION_URI, timeoutMS=5000)
        db = self._mongodb_client[ss.MONGODB_DB]
        self.book_collection = db[ss.MONGODB_BOOK_COLLECTION]
        self.changelog_collection = db[ss.MONGODB_CHANGELOG_COLLECTION]
        self.crawler_state_collection = db[ss.MONGODB_CRAWLER_STATE_COLLECTION]

        self.crawler_state = {}  # Save to database if run ends prematurely
        self.stored_books = {}  # Books already in the db from past crawler runs; used in scheduler runs
        if self.is_scheduler:
            current_date = str(datetime.now().date()).replace("-", "")
            self.snapshot_folder = ss.BASE_FOLDER / "snapshots" / "scheduler" / current_date
        else:
            self.snapshot_folder = ss.BASE_FOLDER / "snapshots" / "crawler"
        self.snapshot_folder.mkdir(parents=True, exist_ok=True)
    
    # Put in scheduler job code
    async def get_current_books(self):
        async for book in self.book_collection.find({}, ss.CHANGE_DETECTION_FIELDS):
            self.stored_books[book["bts_id"]] = book

    async def worker(self, wid: int):
        while not self.shutdown_event.is_set():
            session = None
            try:
                try:
                    session: Session = await asyncio.wait_for(
                        self.queue.get(), ss.QUEUE_WAIT_TIMEOUT_SECONDS
                    )
                except asyncio.TimeoutError:
                    if not self.shutdown_event.is_set():
                        self.logger.info(f"[manager] No new queue entry for {ss.QUEUE_WAIT_TIMEOUT_SECONDS} seconds.")
                        self.logger.info("[manager] Shutting down workers...")
                        self.shutdown_event.set()
                    continue

                worker_log_id = f"[{wid}][{session.resource_type}][{session.sid}]"
                initial_message = self._get_initial_worker_message(session.retry_count)
                self.logger.info(f"{worker_log_id} {initial_message}")

                async with AsyncClient(
                    follow_redirects=True, proxy=ss.PROXY,
                    timeout=ss.REQUEST_TIMEOUT_SECONDS,
                ) as client:
                    try:
                        if session.resource_type == "page":
                            book_count, book_urls = await fetch_page(client, session.resource_url)

                            if self.env == "prod":  # Scrape only a single page if env is "dev"
                                if session.resource_id == 1:
                                    page_count = math.ceil(book_count / len(book_urls))
                                    for i in range(2, page_count+1):
                                        page_session = Session(
                                            sid=f"p{i}",
                                            resource_id=i,
                                            resource_type="page",
                                            resource_url=f"{ss.BASE_URL}/page-{i}.html"
                                        )
                                        await self.queue.put(page_session)
                                        self.crawler_state[page_session.sid] = asdict(page_session)

                            for url in book_urls:
                                book_id = extract_id_from_book_url(url)
                                book_session = Session(
                                    sid=f"b{book_id}",
                                    resource_id=book_id,
                                    resource_type="book",
                                    resource_url=url,
                                )
                                await self.queue.put(book_session)
                                self.crawler_state[book_session.sid] = asdict(book_session)
                        else:
                            if self.is_scheduler:  # Retrieve last etag for the book
                                stored_book = self.stored_books.get(session.resource_id)
                                last_etag = stored_book["crawl_metadata"]["etag"]
                            else:
                                last_etag = None
                            etag, book = await fetch_book(
                                client,
                                session.resource_id, session.resource_url,
                                last_etag, self.snapshot_folder
                            )
                            await self._push_to_storage(session, etag, book)

                        self.crawler_state.pop(session.sid)
                        await self.track_run_status(True)

                    except HTTPError as exc:
                        self.logger.warning(f"[{worker_log_id}] ❌ {repr(exc)}")
                        if session.retry_count < self.max_retry_count:
                            session.retry_count += 1
                            await self.queue.put(session)
                            self.logger.info(f"[{worker_log_id}] 🤞 Queued for retry")
                        else:
                            self.logger.warning(f"[{worker_log_id}] Retry limit reached")
                            if (session.resource_type == "book") and (not self.is_scheduler):
                                self.logger.info(f"[{worker_log_id}] Saving with failed status...")
                                await self._push_to_storage(session, None, None)
                        await self.track_run_status(False)

                    except ProcessingError as exc:  # No retry on processing errors
                        self.logger.exception(f"[{worker_log_id}] ❌ {repr(exc)}")
                        if (session.resource_type == "book") and (not self.is_scheduler):
                            self.logger.info(f"[{worker_log_id}] Saving with failed status...")
                            await self._push_to_storage(session, None, None)
                        await self.track_run_status(False)

            except Exception as exc:
                self.logger.exception(f"[{wid}] ❌ {repr(exc)}")
                await self.track_run_status(False)
            finally:
                if session:
                    self.queue.task_done()
        else:
            self.logger.info(f"[manager] Worker {wid} stopped")

    def _get_initial_worker_message(self, retry_count: int):
        if not retry_count:
            return "Start"
        else:
            return f"Retry {retry_count}"

    async def track_run_status(self, success: bool = True):
        async with self.run_status_lock:
            if not self.shutdown_event.is_set():
                if success:
                    self.consecutive_failures = 0
                else:
                    self.consecutive_failures += 1
                
                if self.consecutive_failures > self.max_consecutive_failures:
                    self.logger.warning("[manager] Maximum consecutive failures reached.")
                    self.logger.info("[manager] Shutting down workers...")
                    self.shutdown_event.set()

    async def _push_to_storage(self, session: Session, etag: Optional[str], book: Optional[Book]):
        if self.is_scheduler and (not book):  # Book hasn't been updated
            self.logger.info(f"[manager] Unchanged: {session.sid}")
            return
        
        document = book.model_dump(mode="json") if book else {"bts_id": session.resource_id}
        timestamp = datetime.now(timezone.utc)
        document["crawl_metadata"] = {
            "timestamp": timestamp,
            "status": "success" if book else "failed",
            "source_url": session.resource_url,
            "etag": etag or ""  # ensure that it is not None
        }

        if not self.is_scheduler:
            # Use replace_one instead of insert_one to avoid possible duplicate key error on bts_id.
            # The error can occur because while a crawl that fails is stored in the book collection,
            # it is not removed from the crawler state. It will be tried again if the user runs the
            # crawler with restart=False.
            await self.book_collection.replace_one(
                filter={"bts_id": document["bts_id"]},
                replacement=document,
                upsert=True
            )
            self.logger.info(f"[manager] ✔ Pushed to storage: {session.sid}")
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

    async def close_db_client(self):
        await self._mongodb_client.close()
