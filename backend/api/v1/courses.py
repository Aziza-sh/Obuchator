from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user
from db.models.base import get_db
from db.models.users import User
from schemas.courses import (
    CourseCreate,
    CourseListItem,
    CourseMaterialCreate,
    CourseMaterialResponse,
    CourseResponse,
)
from services.courses import (
    add_material,
    create_course,
    get_all_courses,
    get_course_by_id,
    is_subscribed,
    subscribe_to_course,
    unsubscribe_from_course,
)

router = APIRouter(prefix="/courses", tags=["courses"])

_COURSE_NOT_FOUND = "Курс не найден"


@router.get("/", response_model=List[CourseListItem])
async def list_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    courses = await get_all_courses(db)
    result = []
    for course in courses:
        subscribed = await is_subscribed(db, current_user.id, course.id)
        result.append(
            CourseListItem(
                id=course.id,
                name=course.name,
                description=course.description,
                teacher_id=course.teacher_id,
                created_at=course.created_at,
                material_count=len(course.materials),
                is_subscribed=subscribed,
            )
        )
    return result


@router.post("/", response_model=CourseResponse, status_code=201)
async def create_course_endpoint(
    data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = await create_course(db, data, current_user.id)
    return CourseResponse(
        id=course.id,
        name=course.name,
        description=course.description,
        teacher_id=course.teacher_id,
        created_at=course.created_at,
        materials=[],
        is_subscribed=False,
    )


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = await get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail=_COURSE_NOT_FOUND)

    subscribed = await is_subscribed(db, current_user.id, course_id)
    return CourseResponse(
        id=course.id,
        name=course.name,
        description=course.description,
        teacher_id=course.teacher_id,
        created_at=course.created_at,
        materials=course.materials,
        is_subscribed=subscribed,
    )


@router.post("/{course_id}/materials", response_model=CourseMaterialResponse, status_code=201)
async def add_course_material(
    course_id: UUID,
    data: CourseMaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = await get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail=_COURSE_NOT_FOUND)

    if course.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только преподаватель курса может добавлять материалы")

    material = await add_material(db, course_id, data)
    return material


@router.post("/{course_id}/subscribe")
async def subscribe(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    course = await get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail=_COURSE_NOT_FOUND)

    return await subscribe_to_course(db, current_user.id, course_id)


@router.delete("/{course_id}/subscribe")
async def unsubscribe(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await unsubscribe_from_course(db, current_user.id, course_id)
