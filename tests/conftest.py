import os
from typing import Generator, AsyncGenerator
import asyncio
import pytest
import pytest_asyncio
from async_asgi_testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from app.main import app
from app.database.database import engine

@pytest_asyncio.fixture(autouse=True, scope="session")
async def setup_database():
    # alembic.config.main(argv=['--raiseerr', 'upgrade', 'head'])  # causes nested event loop?
    os.system("alembic upgrade head")
    yield
    async with engine.begin() as conn:
        await conn.execute(text("drop schema public cascade"))
        await conn.execute(text("create schema public"))


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[TestClient, None]:
    host, port = "127.0.0.1", "8000"
    scope = {"client": (host, port)}

    async with TestClient(app, scope=scope) as client:
        yield client


@pytest_asyncio.fixture(scope="session")
async def session(setup_database) -> AsyncGenerator[AsyncSession, None]:
    from app.database.database import get_session
    async with get_session() as session:
        yield session

