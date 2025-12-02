import logging
import time
from datetime import datetime, timezone
from typing import Literal

from ..settings import BASE_FOLDER

def setup_logging(run_type: Literal["crawler", "scheduler"]):
    log_folder = BASE_FOLDER / "logs"
    log_folder.mkdir(exist_ok=True)

    logger = logging.getLogger(run_type)
    logger.setLevel(logging.INFO)

    logger.handlers.clear()

    # Stdout handler
    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.INFO)

    # File handler
    time_now = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    log_file = log_folder / f"{run_type}_{time_now}.log"
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
