from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from db.models import Base
from sqlalchemy import ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CourseMaterial(Base):
    __tablename__ = "course_materials"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"))
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    material_type: Mapped[str] = mapped_column(nullable=False, default="material")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    course: Mapped["Course"] = relationship(back_populates="materials")
