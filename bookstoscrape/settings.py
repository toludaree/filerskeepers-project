import os
from pymongo import AsyncMongoClient
from dotenv import load_dotenv


load_dotenv()

BASE_URL = "https://books.toscrape.com/catalogue"
PROXY = None
REQUEST_TIMEOUT = 5
BROWSER_HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "naviagate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
}
BOOK_RATING_MAPPER = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}
MONGODB_CONNECTION_URI = os.getenv("MONGODB_CONNECTION_URI")
MONGODB_DB = os.getenv("MONGODB_DB")
MONGODB_BOOK_COLLECTION = os.getenv("MONGODB_BOOK_COLLECTION")
MONGODB_CHANGELOG_COLLECTION = os.getenv("MONGODB_CHANGELOG_COLLECTION")

ASYNC_MONGODB_DB = AsyncMongoClient(MONGODB_CONNECTION_URI, timeoutMs=5000)[MONGODB_DB]

CHANGE_DETECTION_FIELDS = {
    "_id": 0,
    "bts_id": 1,
    "price_excluding_tax": 1,
    "price_including_tax": 1,
    "stock_count": 1,
    "review_count": 1,
    "rating": 1,
    "crawl_metadata.etag": 1,
    "crawl_metadata.source_url": 1
}
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")