from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class NewsCreate(BaseModel):

    title: str
    category: str
    excerpt: str
    content: str
    author: UUID


class NewsResponse(BaseModel):

    id: UUID
    title: str
    category: str
    excerpt: str
    content: str
    author_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
