from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from db.models.base import Base
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    password_hash: Mapped[str]
    is_admin: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    role: Mapped[str] = mapped_column(default="student")
    is_active: Mapped[bool] = mapped_column(default=True)
    news: Mapped[List["News"]] = relationship(back_populates="author")
