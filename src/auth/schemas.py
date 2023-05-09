from typing import Optional
from datetime import datetime
from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    id: int
    tg_id: int
    username: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    api_key: str
    task_avail: int
    last_task_at: Optional[datetime]

    email: str = "stub@mail.com"

    class Config:
        orm_mode = True


class UserCreate(schemas.BaseUserCreate):
    username: str
    tg_id: int
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

    email: str = "stub@mail.com"
