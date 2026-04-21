from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from db.models import Base
from sqlalchemy import ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    teacher_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    teacher: Mapped["User"] = relationship()
    materials: Mapped[List["CourseMaterial"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
    subscriptions: Mapped[List["CourseSubscription"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
