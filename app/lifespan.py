from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from starlette.applications import Starlette

from app.database.database import engine
from app.resources import broadcast


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncGenerator[None, None]:
    try:
        async with engine.begin() as conn:
            # healthcheck
            await conn.execute(text("SELECT 1"))
        await broadcast.connect()
        yield

    except Exception:
        await engine.dispose()
        await broadcast.disconnect()
        raise
