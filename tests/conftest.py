import pytest
import asyncio
import logging

from fastapi.testclient import TestClient
from typing import AsyncGenerator
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from database import get_async_session
from src import metadata
from src.config import (
    POSTGRE_URL_TEST,
    POSTGRE_URL,
)

from src.main import app

# DATABASE
DATABASE_URL_TEST = POSTGRE_URL_TEST


engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
metadata.bind = engine_test
logging.error(f"metadata database {metadata.tables}")

async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    logging.error("call override_get_async_session")
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session

@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    logging.error("run db prepare")
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.create_all)
        logging.error("created all")
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        logging.error("dropped all")

# SETUP
@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

client = TestClient(app)

@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
