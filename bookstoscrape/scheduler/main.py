import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore

from .job import bts_scheduler


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(bts_scheduler, "interval", seconds=30)
    scheduler.start()

    print("Scheduler started. Press CTRL+C to exit.")

    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
