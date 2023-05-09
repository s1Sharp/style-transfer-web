from datetime import datetime
import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    ForeignKey,
    Enum
)
from database import metadata, Base

from auth.models import User

class TaskState(enum.Enum):
    queued: str = "queued"
    started: str = "started"
    finished: str = "finished"


class Task(Base):
    __tablename__ = "task"

    id: int = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    status = Column(Enum(TaskState, native_enum=False, length=16), nullable=True, default=TaskState.queued)
    style_name: str = Column(String(length=512), nullable=False)
    src_image_name: str = Column(String(length=512), nullable=True)
    dst_image_name: str = Column(String(length=512), nullable=True)
    download_link: str = Column(String(length=512), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    started_at = Column(TIMESTAMP, nullable=True)
    finished_at = Column(TIMESTAMP, nullable=True)
    expire_at = Column(TIMESTAMP, nullable=True)


task_table = Task.__table__