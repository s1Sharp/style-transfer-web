from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from config import env_control
from task.s3storage import S3StyleStorage

DATABASE_URL = env_control.POSTGRE_URL

metadata = MetaData()
Base = declarative_base(metadata=metadata)

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

S3_ENDPOINT = env_control.S3_ENDPOINT
S3_ACCESS_KEY_ID = env_control.S3_ACCESS_KEY_ID
S3_SECRET_ACCESS_KEY = env_control.S3_SECRET_ACCESS_KEY

s3storage = S3StyleStorage(S3_ENDPOINT, S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY)
