import asyncio
import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from httpx import AsyncClient, HTTPError
from logging import Logger
from pymongo import AsyncMongoClient
from typing import Literal, Optional

from .. import settings as ss
from ..utils.common import Book
from ..utils.crawler import extract_id_from_book_url
from ..utils.scheduler import send_alert_email
from .exceptions import ProcessingError
from .fetch import fetch_page, fetch_book


@dataclass
class Session:
    sid: str  # session id
    resource_id: int
    resource_type: Literal["page", "book"]
    resource_url: str
    retry_count: int = 0

class Manager:
    def __init__(
        self,
        env: Literal["dev", "prod"], logger: Logger,
        is_scheduler: bool = False
    ):
        self.queue = asyncio.Queue()
        self.workers: list[asyncio.Task] = []
        self.env = env
        self.logger = logger
        self.is_scheduler = is_scheduler
        self.consecutive_failures = 0
        self.run_status_lock = asyncio.Lock()
        self.shutdown_event = asyncio.Event()

        self._mongodb_client = AsyncMongoClient(ss.MONGODB_CONNECTION_URI, timeoutMS=5000)
        db = self._mongodb_client[ss.MONGODB_DB]
        self.book_collection = db[ss.MONGODB_BOOK_COLLECTION]
        self.changelog_collection = db[ss.MONGODB_CHANGELOG_COLLECTION]
        self.crawler_state_collection = db[ss.MONGODB_CRAWLER_STATE_COLLECTION]

        self.current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.crawler_state = {}  # Save to database if run ends prematurely
        
        if self.is_scheduler:
            self.snapshot_folder = ss.BASE_FOLDER / "snapshots" / "scheduler" / self.current_date.replace("-", "")
        else:
            self.snapshot_folder = ss.BASE_FOLDER / "snapshots" / "crawler"
        self.snapshot_folder.mkdir(parents=True, exist_ok=True)
        
        self.stored_books = {}  # Books already in the db from past crawler runs; used in scheduler runs
        self.daily_change_report = None  # Used in scheduler runs

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
                        self.logger.info(f"[manager] No new queue entry for {ss.QUEUE_WAIT_TIMEOUT_SECONDS} seconds...")
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
                            
                            self.logger.info(f"{worker_log_id} Processed page successfully")
                        else:
                            # Retrieve last etag for the book
                            if self.is_scheduler:
                                stored_book = self.stored_books.get(session.resource_id)
                                if stored_book:
                                    last_etag = stored_book["crawl_metadata"]["etag"]
                                else:
                                    last_etag = None
                            else:
                                last_etag = None

                            etag, book = await fetch_book(
                                client,
                                session.resource_id, session.resource_url,
                                last_etag, self.snapshot_folder
                            )
                            await self._push_to_storage(
                                session.resource_id, session.resource_url,
                                etag, book
                            )

                        self.crawler_state.pop(session.sid)
                        await self.track_run_status(True)

                    except HTTPError as exc:
                        self.logger.warning(f"{worker_log_id} Error: {repr(exc)}")
                        if session.retry_count < ss.MAX_RETRY_COUNT:
                            session.retry_count += 1
                            await self.queue.put(session)
                            self.logger.info(f"{worker_log_id} Queued for retry")
                        else:
                            self.logger.warning(f"{worker_log_id} Retry limit reached")
                            if (session.resource_type == "book") and (not self.is_scheduler):
                                self.logger.info(f"{worker_log_id} Saving with failed status...")
                                await self._push_to_storage(
                                    session.resource_id, session.resource_url,
                                    None, None
                                )
                        await self.track_run_status(False)

                    except ProcessingError as exc:  # No retry on processing errors
                        self.logger.exception(f"{worker_log_id} Error: {repr(exc)}")
                        if (session.resource_type == "book") and (not self.is_scheduler):
                            self.logger.info(f"{worker_log_id} Saving with failed status...")
                            await self._push_to_storage(
                                session.resource_id, session.resource_url,
                                None, None
                            )
                        await self.track_run_status(False)

            except Exception as exc:
                self.logger.exception(f"[{wid}] Error: {repr(exc)}")
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
                
                if self.consecutive_failures > ss.MAX_CONSECUTIVE_FAILURES:
                    self.logger.warning("[manager] Maximum consecutive failures reached.")
                    self.logger.info("[manager] Shutting down workers...")
                    self.shutdown_event.set()

    async def _push_to_storage(
        self,
        book_id: int, book_url: str, etag: Optional[str], book: Optional[Book]
    ):
        if self.is_scheduler and (not book):  # Book hasn't been updated
            self.logger.info(f"[manager] Unchanged: {book_id}")
            return
        
        document = book.model_dump(mode="json") if book else {"bts_id": book_id}
        timestamp = datetime.now(timezone.utc)
        document["crawl_metadata"] = {
            "timestamp": timestamp,
            "status": "success" if book else "failed",
            "source_url": book_url,
            "etag": etag
        }

        # replace_one works for both normal crawler and scheduler runs.
        # In a normal crawler run, we want to prevent duplicate key error on bts_id
        # when failed crawls, stored in the book collection, are retried through restart=False.
        # For scheduler runs, update_one is not ideal since the $set and $setOnInsert fields
        # are not fixed.
        result = await self.book_collection.replace_one(
            filter={"bts_id": document["bts_id"]},
            replacement=document,
            upsert=True
        )

        if not self.is_scheduler:
            self.logger.info(f"[manager] Pushed to storage: {book_id}")
        else:
            if result.did_upsert:
                self.logger.info(f"[manager] Book added: {book_id}")
                event = "add"
                self.daily_change_report["summary"]["added"] += 1
                changes = {}
            else:
                self.logger.info(f"[manager] Book updated: {book_id}")
                event = "update"
                self.daily_change_report["summary"]["updated"] += 1
                changes = self._get_update_changes(book.model_dump(mode="json"))
            self.daily_change_report["summary"]["total"] += 1

            changelog_doc = {
                "bts_id": book_id,
                "event": event,
                "timestamp": timestamp,
                "changes": changes
            }
            await self.changelog_collection.insert_one(dict(changelog_doc))

            changelog_doc["timestamp"] = changelog_doc["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            self.daily_change_report["changelog"].append(changelog_doc)
                
            try:
                await asyncio.to_thread(send_alert_email, event, book_id)
                self.logger.info(f"[manager] Alert email sent for {event} event: {book_id}")
            except Exception as exc:
                self.logger.warning(f"[manager] Failed to send alert email for {book_id}: {repr(exc)}")

    def _get_update_changes(self, book: dict):
        changes = {}
        old_version: dict = self.stored_books[book["bts_id"]]

        for k in old_version.keys():
            if k in ("bts_id", "crawl_metadata"):
                continue
            if (old:=old_version[k]) != (new:=book[k]):
                changes[k] = {"old": old, "new": new}
        
        return changes

    async def close_db_client(self):
        await self._mongodb_client.close()
