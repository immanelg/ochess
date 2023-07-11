from contextlib import asynccontextmanager

from starlette.applications import Starlette

from app.resources import broadcast


@asynccontextmanager
async def lifespan(app: Starlette):
    try:
        await broadcast.connect()
        yield
    except Exception as e:
        await broadcast.disconnect()
        raise e
