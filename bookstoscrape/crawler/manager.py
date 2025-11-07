import json
from asyncio import Queue, Task
from dataclasses import dataclass
from logging import Logger
from pathlib import Path
from typing import Literal, Optional

from .models import Book


@dataclass
class PageSession:
    sid: int
    page_num : int
    page_url: str
    retry_count: int = 0

@dataclass
class BookSession:
    sid: int
    book_url: str
    result: Optional[Book] = None
    retry_count: int = 0

class Manager:
    def __init__(self, logger: Logger, env: Literal["dev", "prod"]):
        self.queue = Queue()
        self.workers: list[Task] = []
        self.logger = logger
        self.env =  env
        self.storage_dev_path = Path("C:/Users/Isaac/Desktop/me/jobs/filerskeepers/project/storage_dev")

    def cleanup(self, session: BookSession):
        if self.env == "dev":
            with open(self.storage_dev_path / f"{session.sid}.json", "w") as f:
                json.dump(session.result.model_dump(), f)
