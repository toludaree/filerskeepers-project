import logging
import smtplib
import time
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Literal

from .. import settings as ss

def setup_logger(name: Literal["crawler", "scheduler"]):
    log_folder = ss.BASE_FOLDER / "logs"
    log_folder.mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    logger.handlers.clear()

    # Stdout handler
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.INFO)

    # File handler
    time_now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    log_file = log_folder / f"{name}_{time_now}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    formatter.converter = time.gmtime
    stdout_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(stdout_handler)
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
