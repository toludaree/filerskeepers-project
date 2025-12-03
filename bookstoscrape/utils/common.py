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

from ..settings import (
    ADMIN_EMAIL, BASE_FOLDER, EMAIL_PASSWORD, EMAIL_SENDER, EMAIL_SMTP_PORT,
    EMAIL_SMTP_SERVER,
)


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
    "Academic", "Add a comment", "Adult Fiction", "Art", "Autobiography",
    "Biography", "Business", "Childrens", "Christian", "Christian Fiction",
    "Classics", "Contemporary", "Crime", "Cultural", "Default", "Erotica",
    "Fantasy", "Fiction", "Food and Drink", "Health", "Historical",
    "Historical Fiction", "History", "Horror", "Humor", "Music", "Mystery",
    "New Adult", "Nonfiction", "Novels", "Paranormal", "Parenting",
    "Philosophy", "Poetry", "Politics", "Psychology", "Religion", "Romance",
    "Science", "Science Fiction", "Self Help", "Sequential Art",
    "Short Stories", "Spirituality", "Sports and Games", "Suspense",
    "Thriller", "Travel", "Womens Fiction", "Young Adult"
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
        log_folder = BASE_FOLDER / "logs"
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
    msg["From"] = f"BooksToScrape <{EMAIL_SENDER}>"
    msg["To"] = ADMIN_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
