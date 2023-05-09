from typing import Any, Callable, List
from enum import Enum

from fastapi import BackgroundTasks

class TaskStarterEnum(str, Enum):
    celery_task = 'celery'
    worker_task = 'worker'

class CeleryTaskAdapter:
    def __init__(self,
        task: Callable,
        task_config: TaskStarterEnum = TaskStarterEnum.celery_task,
    ):
        self.task: Callable = task
        self.config: TaskStarterEnum = task_config
        self.background_tasks = None

    def __call__(self,*, backend: BackgroundTasks = None):
        self.background_tasks = backend
        return self

    def add_new_task_to_queue(self, *args, **kwargs):
        if self.config == TaskStarterEnum.celery_task:
            self.task.delay(*args, **kwargs)
        elif self.config == TaskStarterEnum.worker_task:
            self.background_tasks.add_task(self.task, *args, **kwargs)
