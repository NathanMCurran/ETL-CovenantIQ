from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers.transform_router import router as transform_router
from app.services import database as db


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="ETL FastAPI Project", lifespan=lifespan)

app.include_router(transform_router)
