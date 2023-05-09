from datetime import datetime, timedelta

from task.models import Task, TaskState
from task.style_config import net

from sqlalchemy import select
from database import s3storage, async_session_maker
from config import REDIS_URL

from celery import Celery
import asyncio

s3_proxy = s3storage.s3_proxy

celery = Celery('tasks', broker=REDIS_URL)


async def make_convert_image_impl(task_id: int):
    async with async_session_maker() as session:
        try:
            started_at = datetime.utcnow()
            task = await session.get(Task, task_id)
            # validate api_key
            if task is None:
                err_message = f"fail get task by task id {task_id}"
                raise Exception(err_message)

            print(f"task {task_id}")
            bin_file = s3_proxy.download_file_binary(task.src_image_name)

            output_binary_file = net.create_image_test(bin_file)

            output_file_key = f"images/dst/{task.user_id}/{task.created_at}.jpg"
            net.s3.upload_file_binary(output_binary_file, output_file_key)
            file_link = net.s3.get_object_presigned_url(output_file_key)
            net.s3.delete_files(task.src_image_name)

            task.download_link = file_link
            task.started_at = started_at
            task.finished_at = datetime.utcnow()
            task.expire_at = task.created_at + timedelta(days=1)
            task.status = TaskState.finished
            task.dst_image_name = output_file_key
            task.src_image_name = None

            session.add(task)
            await session.commit()
            print('file uploaded')

        except Exception as e:
            print(f'error {e}')


@celery.task
def make_convert_image(task_id: int):
    asyncio.run(make_convert_image_impl(task_id))

from task.task_adapter import CeleryTaskAdapter, TaskStarterEnum
task_adapter = CeleryTaskAdapter(make_convert_image, TaskStarterEnum.celery_task)