from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routes import audio, images, operations
from app.services.queue import extraction_queue


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    await extraction_queue.start()
    try:
        yield
    finally:
        await extraction_queue.stop()


app = FastAPI(title="Finance Tracker", lifespan=lifespan)
app.include_router(images.router)
app.include_router(audio.router)
app.include_router(operations.router)
