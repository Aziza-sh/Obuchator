from __future__ import annotations

from datetime import datetime
from uuid import UUID

from db.models import Base
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class NewsView(Base):
    __tablename__ = "news_views"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    news_id: Mapped[UUID] = mapped_column(ForeignKey("news.id"))
    viewed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    news: Mapped["News"] = relationship(back_populates="views")
