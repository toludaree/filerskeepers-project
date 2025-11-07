import json
import logging
from asyncio import Queue, Task
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

from .models import Book


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
    # result: Optional[Book] = None
    retry_count: int = 0

class Manager:
    def __init__(self, env: Literal["dev", "prod"], max_retry_count: int):
        self.queue = Queue()
        self.workers: list[Task] = []
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.env =  env
        self.max_retry_count = max_retry_count
        self.storage_dev_path = Path("C:/Users/Isaac/Desktop/me/jobs/filerskeepers/project/storage_dev")

    def cleanup(self, result: Book, sid: int):
        if self.env == "dev":
            with open(self.storage_dev_path / f"{sid}.json", "w") as f:
                json.dump(result.model_dump(mode="json"), f)
        self.logger.info(f"[manager] Ready: {sid}")
