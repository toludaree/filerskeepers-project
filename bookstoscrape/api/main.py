from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from ..utils.api import lifespan
from .routers.auth import router as auth_router
from .routers.book import router as book_router


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(book_router)

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    """Check the health of the database"""
    try:
        await app.mongodb_client.admin.command("ping")
        stats = await app.db.command("dbStats")
        return {
            "status": "healthy",
            "database": stats.get("db"),
            "collections": stats.get("collections", 0)
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "error": str(exc)
        }
