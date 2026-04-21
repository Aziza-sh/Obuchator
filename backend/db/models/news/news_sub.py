from __future__ import annotations

from uuid import UUID, uuid4

from db.models import Base
from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class NewsSubscription(Base):
    __tablename__ = "news_subscriptions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship()

    __table_args__ = (UniqueConstraint("user_id", name="uq_news_subscription_user"),)
