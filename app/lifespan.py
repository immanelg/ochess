from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from starlette.applications import Starlette

from app.database.database import engine
from app.logging import logger
from app.resources import broadcast


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncGenerator[None, None]:
    try:
        logger.info("DB healthcheck")
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        logger.info("connect broadcast")
        await broadcast.connect()

        logger.info("starting app")
        yield

    except Exception:
        await engine.dispose()
        await broadcast.disconnect()
        raise
