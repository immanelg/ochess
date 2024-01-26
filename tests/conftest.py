from typing import Generator, AsyncGenerator
import asyncio

import pytest
import pytest_asyncio
from async_asgi_testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database.database import engine


@pytest.fixture(scope="session", autouse=True)
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True, scope="session")
async def setup_database():
    # TODO: use alembic 
    from app.database.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        pass

    await engine.dispose()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[TestClient, None]:
    host, port = "127.0.0.1", "8000"
    scope = {"client": (host, port)}

    async with TestClient(app, scope=scope) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def session() -> AsyncGenerator[AsyncSession, None]:
    from app.database.database import get_session
    async with get_session() as session:
        yield session

