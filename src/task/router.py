import time
import hashlib

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, File, Request, Response, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_cache.coder import JsonCoder 
from starlette import status

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from auth.models import User
from task.models import Task, TaskState
from task.schemas import TaskCreate, TaskRead
from task.manager import get_task_manager, get_user_id_by_api_key, put_file_into_bucket, validate_filebytes_size
from task.style_config import StyleNames, get_style_name
from task.tasks import make_convert_image, task_adapter


router = APIRouter(
    prefix="/task",
    tags=["Tasks"]
)


@router.get("/task_operation")
@cache(expire=3600)
def get_long_op():
    time.sleep(5)
    return "Тестовый роут для исследовани cache"


@router.get("")
async def get_specific_task(
    task_id: int,
    api_key: str,
    session: AsyncSession = Depends(get_async_session),
    user_id: Optional[int] = Depends(get_user_id_by_api_key),
):
    try:
        task = await session.get(Task, task_id)
        # validate api_key
        if task is None:
            return {
                "status": 404,
                "data": "task id not found",
                "details": None
            }
        user = await session.get(User, task.user_id)
        if user.api_key != api_key:
            return {
                "status": 403,
                "data": "incorrect api_key",
                "details": None
            }

        task_read_obj = TaskRead(status=task.status, download_link=task.download_link, expire_at=task.expire_at)

        return {    
            "status": "success",
            "data": task_read_obj,
            "details": None
        }

    except Exception as e:
        print(f'error {e}')
        # Передать ошибку разработчикам
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })



@router.post("/{style_name}")
async def add_specific_task(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None, 
    session: AsyncSession = Depends(get_async_session),
    user: Optional[User] = Depends(get_user_id_by_api_key),
    style_name: str = Depends(get_style_name),
    ):
    if user is None:
        return {
            "status": 403,
            "data": None,
            "details": "incorrect api_key"
        }

    created_at = datetime.utcnow()
    if user.task_avail < 5:
        # time_delta_from_last_task
        tdflt = created_at - user.last_task_at
        tdflt_in_sec = tdflt.total_seconds()
        days_div = divmod(tdflt_in_sec, 86400)[0]
        print(f"div in seconds = {tdflt_in_sec}")
        if user.task_avail <= 0:
            if days_div > 0:
                user.task_avail = 5
            else:
                return {
                    "status": 422,
                    "data": None,
                    "details": "not available task for today"
                }
        else:
            if days_div > 0:
                user.task_avail = 5
    
    user.task_avail -= 1
    user.last_task_at = created_at
            
    filepath = f"images/src/{user.id}/{created_at}.jpg"

    filebytes = file.file.read()
    if validate_filebytes_size(filebytes):
        print(put_file_into_bucket(filebytes, filepath))
    else:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Too large",
        )


    task = Task()
    task.src_image_name = filepath
    task.user_id = user.id
    task.status = TaskState.queued
    task.created_at = created_at
    task.style_name = style_name

    session.add(task)
    session.add(user)
    await session.commit()

    task_adapter(backend=background_tasks).add_new_task_to_queue(task.id)

    return {
        "status": 200,
        "data": {"Task created": task.id },
        "details": None
    }

def custom_task_cache(
    func,
    namespace: Optional[str] = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
):
    prefix = FastAPICache.get_prefix()
    route_args = kwargs['kwargs']
    param_key = f"{route_args['task_id']}:{route_args['api_key']}"
    hashed_param_key = hashlib.sha1(param_key.encode('utf-8')).hexdigest()
    cache_key = f"{prefix}:{namespace}:{func.__module__}:{func.__name__}:{hashed_param_key}"
    return cache_key


@router.get("/task_status")
@cache(expire=60 * 60 * 24, coder=JsonCoder, key_builder=custom_task_cache) # lambda *arg,**kwargs: kwargs['response'].body
async def get_task_status(task_id: int, api_key: str, session: AsyncSession = Depends(get_async_session)): # task=Depends(get_task_manager)):
    print("task_working")
    task = await session.get(Task, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    user = await session.get(User, task.user_id)
    if user.api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect api_key",
        )

    return JSONResponse(
        status_code=200, 
        content={
            "data": {"task_status": task.status.value, "task_link": task.download_link},
            "details": None
        }
    )
