from __future__ import annotations

from uuid import UUID, uuid4

from db.models import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CourseSubscription(Base):
    __tablename__ = "course_subscriptions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"))

    course: Mapped["Course"] = relationship(back_populates="subscriptions")
    user: Mapped["User"] = relationship()

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_course_subscription"),
    )
