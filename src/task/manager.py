import aiofiles
from typing import Optional

from fastapi import Depends, Request, UploadFile, HTTPException
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users import (
    BaseUserManager,
    IntegerIDMixin,
    exceptions,
    models,
    schemas
)

from config import SECRET_AUTH

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session, s3storage
from auth.models import User
from task.models import Task


async def get_task_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, Task)

async def get_user_id_by_api_key(api_key: str, session: AsyncSession = Depends(get_async_session)) -> Optional[int]:
    try:
        query = select(User).where(User.api_key == api_key)
        result = await session.execute(query)
        data = result.first()
        if data is not None:
            return data[0]
        else:
            return None
    except Exception as e:
        print(f'error {e}')
        return None


def put_file_into_bucket(file_bytes: bytes, s3filepath: str):
    return s3storage.put_src_file(file_bytes, s3filepath)


class TaskManager():

    def __init__(self, task_db):
        self.task_db = task_db
        self.on_after_create(self.task_db)

    def on_after_create(self, task: Task):
        print(f"Task {task.id} has created.")

async def get_task_manager(task_db=Depends(get_task_db)):
    yield TaskManager(task_db)



def validate_filebytes_size(file: bytes, max_file_size: int = 1024 * 1024 * 5) -> bool: # 5 MB
    return len(file) <= max_file_size

async def validate_file_size(file: UploadFile, max_file_size: int = 1024 * 1024 * 5) -> bool: # 5 MB
    real_file_size = 0

    try:
        async with aiofiles.open("/tmp/fastapi_app_tmpfileanme", "wb") as out_file:
            while content := await file.read(1024):  # async read chunk
                real_file_size += len(content)
                if real_file_size > max_file_size:
                    return False
                # await out_file.write(content)  # async write chunk
        msg = f"Successfuly uploaded {file.filename} for processing"
        print(msg)
        return True
    except IOError:
        return False
