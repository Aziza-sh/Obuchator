from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuthorShort(BaseModel):
    id: UUID
    first_name: str
    last_name: str


class NewsCreate(BaseModel):

    title: str
    category: str
    excerpt: str
    content: str


class NewsResponse(BaseModel):

    id: UUID
    title: str
    category: str
    excerpt: str
    content: str
    author_id: UUID
    created_at: datetime
    author: AuthorShort
    likes_count: int
    is_liked: bool

    class Config:
        from_attributes = True
