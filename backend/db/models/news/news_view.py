from __future__ import annotations
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.models import Base


class NewsView(Base):
    __tablename__ = "news_views"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    news_id: Mapped[UUID] = mapped_column(ForeignKey("news.id"))
    viewed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    news: Mapped["News"] = relationship(back_populates="views")
