from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from db.models import Base
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class News(Base):
    __tablename__ = "news"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str]
    excerpt: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="news")
    likes: Mapped[List["NewsLike"]] = relationship(back_populates="news")
    views: Mapped[List["NewsView"]] = relationship(back_populates="news")
