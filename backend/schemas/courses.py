from datetime import datetime
from typing import List, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CourseMaterialCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(default="", max_length=10000)
    material_type: Literal["material", "homework"] = "material"


class CourseMaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    course_id: UUID
    title: str
    description: str
    material_type: str
    created_at: datetime


class CourseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="", max_length=5000)


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
    teacher_id: UUID
    created_at: datetime
    materials: List[CourseMaterialResponse] = []
    is_subscribed: bool = False


class CourseListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str
    teacher_id: UUID
    created_at: datetime
    material_count: int = 0
    is_subscribed: bool = False
