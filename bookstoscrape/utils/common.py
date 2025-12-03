from __future__ import annotations
import logging
import smtplib
import time
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import IntEnum
from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional

from .. import settings as ss


class Book(BaseModel):
    bts_id: int
    name: str
    description: Optional[str]
    url: HttpUrl
    category: Category
    upc: str
    price: float
    tax: float
    in_stock: bool
    stock_count: int
    review_count: int
    cover_image_url: HttpUrl
    rating: Rating

class Rating(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

Category = Literal[
    "Travel", "Mystery", "Historical Fiction", "Sequential Art", "Classics",
    "Philosophy", "Romance", "Women's Fiction", "Fiction", "Childrens",
    "Religion", "Nonfiction", "Music", "Default", "Science Fiction",
    "Sports and Games", "Add a comment", "Fantasy", "New Adult",
    "Young Adult", "Science", "Poetry", "Paranormal", "Art", "Psychology",
    "Autobiography", "Parenting", "Adult Fiction", "Humor", "Horror",
    "History", "Food and Drink", "Christian Fiction", "Business", "Biography",
    "Thriller", "Contemporary", "Spirituality", "Academic", "Self Help",
    "Historical", "Christian", "Suspense", "Short Stories", "Novels",
    "Health", "Politics", "Cultural", "Erotica", "Crime",
]

def setup_logger(
    name: Literal["crawler", "scheduler", "api"],
    add_file_handler: bool = True,
    use_uvicorn_format: bool = False
):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    logger.handlers.clear()

    # Formatter
    if use_uvicorn_format:
        formatter = logging.Formatter(
            fmt="%(levelname)s      %(message)s"
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        formatter.converter = time.gmtime

    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    if add_file_handler:
        log_folder = ss.BASE_FOLDER / "logs"
        log_folder.mkdir(exist_ok=True)
        time_now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        log_file = log_folder / f"{name}_{time_now}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def cleanup_logger(name: Literal["crawler", "scheduler"]):
    """Close all handlers for a logger to release file locks"""
    logger = logging.getLogger(name)
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

def send_email(subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = f"BooksToScrape <{ss.EMAIL_SENDER}>"
    msg["To"] = ss.ADMIN_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(ss.EMAIL_SMTP_SERVER, ss.EMAIL_SMTP_PORT) as server:
        server.starttls()
        server.login(ss.EMAIL_SENDER, ss.EMAIL_PASSWORD)
        server.send_message(msg)
