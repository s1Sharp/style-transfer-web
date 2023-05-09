import secrets
from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Integer, 
    String,
)

from database import Base, metadata


class User(Base):
    __tablename__ = "user"

    id: int = Column(Integer, primary_key=True)
    email = Column(String(length=256), nullable=False)
    tg_id = Column(Integer, default=None, nullable=True)
    username = Column(String, nullable=True) # tg_id if None
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    hashed_password: str = Column(String(length=256), nullable=False)
    password: str = Column(String(length=256), nullable=True)
    api_key: str = Column(String(length=256), default=secrets.token_urlsafe(16), nullable=False)
    task_avail: int = Column(Integer, default=5, nullable=False)
    last_task_at = Column(TIMESTAMP, default=None, nullable=True)

    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)


user_table = User.__table__