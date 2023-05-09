from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from task.models import Task, TaskState


class TaskCreate(BaseModel):
    api_key: str
    style_name: str
    created_at: Optional[datetime] = None

class TaskRead(BaseModel):    
    status: TaskState
    download_link: Optional[str] = None
    expire_at: Optional[datetime] = None
