import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore

from .. import settings as ss
from .job import bts_scheduler


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        bts_scheduler,
        "cron", hour=12, timezone="UTC",  # Run every day at 12 noon UTC
        args=["prod"],
        misfire_grace_time=ss.MISFIRE_GRACE_TIME
    )
    store = MongoDBJobStore(
        database=ss.MONGODB_DB,
        collection=ss.MONGODB_SCHEDULED_JOBS_COLLECTION
    )
    scheduler.add_jobstore(store)
    scheduler.start()

    print("Scheduler started. Press CTRL+C to exit.")

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
