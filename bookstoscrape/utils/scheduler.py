from typing import Literal

from .common import send_email


def send_alert_email(event: Literal["add", "update"], book_id: int):
    """Send alert email when a book is updated or a new book is found"""
    subject = f"[Scheduler Alert] Book {"added" if event == "add" else "updated"}"
    body = f"BooksToScrape ID - {book_id}"
    send_email(subject, body)
