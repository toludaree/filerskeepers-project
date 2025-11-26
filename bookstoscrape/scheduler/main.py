import asyncio
import logging
import threading
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore

from job import bts_scheduler


logging.basicConfig(
    filename="scheduler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def job():
    return bts_scheduler(env="dev")


def start_scheduler():
    # MongoDB job store
    jobstores = {
        "default": MongoDBJobStore(
            host="mongodb://localhost:27017/books",
            collection="scheduled_jobs",
        )
    }

    # AsyncIOScheduler
    scheduler = AsyncIOScheduler(jobstores=jobstores)

    # Add daily job at 5 AM
    scheduler.add_job(
        job,
        trigger="cron",
        hour=4,
        minute=20,
        id="daily_async_job",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started — will run daily at 5 AM")
    print("[Scheduler] Started — running in background...")

    # Keep the scheduler alive
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutting down")
        scheduler.shutdown()


# --------------------------
# Run scheduler in background thread
# --------------------------
# thread = threading.Thread(target=start_scheduler, daemon=True)
# thread.start()

# --------------------------
# Main program does nothing, just waits
# --------------------------
try:
    while True:
        asyncio.sleep(1)
except (KeyboardInterrupt, SystemExit):
    print("\nExiting main program...")
