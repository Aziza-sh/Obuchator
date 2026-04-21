from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.courses.course import Course
from db.models.courses.course_material import CourseMaterial
from db.models.courses.course_subscription import CourseSubscription
from schemas.courses import CourseCreate, CourseMaterialCreate
from services.telegram_bot import send_course_notification

_MATERIAL_TYPE_LABELS = {
    "homework": "Домашнее задание",
    "material": "Материал",
}


async def create_course(db: AsyncSession, data: CourseCreate, teacher_id: UUID) -> Course:
    course = Course(name=data.name, description=data.description, teacher_id=teacher_id)
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


async def get_all_courses(db: AsyncSession) -> list[Course]:
    stmt = select(Course).options(selectinload(Course.materials)).order_by(Course.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_course_by_id(db: AsyncSession, course_id: UUID) -> Course | None:
    stmt = (
        select(Course)
        .where(Course.id == course_id)
        .options(selectinload(Course.materials))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def add_material(
    db: AsyncSession, course_id: UUID, data: CourseMaterialCreate
) -> CourseMaterial:
    course = await get_course_by_id(db, course_id)

    material = CourseMaterial(
        course_id=course_id,
        title=data.title,
        description=data.description,
        material_type=data.material_type,
    )
    db.add(material)
    await db.commit()
    await db.refresh(material)

    subscribers_stmt = (
        select(CourseSubscription)
        .where(CourseSubscription.course_id == course_id)
        .options(selectinload(CourseSubscription.user))
    )
    result = await db.execute(subscribers_stmt)
    subscriptions = result.scalars().all()

    for sub in subscriptions:
        if sub.user and sub.user.telegram_chat_id:
            await send_course_notification(
                chat_id=sub.user.telegram_chat_id,
                course_id=course_id,
                course_name=course.name,
                material_title=material.title,
                material_type=material.material_type,
            )

    return material


async def subscribe_to_course(db: AsyncSession, user_id: UUID, course_id: UUID) -> dict:
    try:
        db.add(CourseSubscription(user_id=user_id, course_id=course_id))
        await db.commit()
        return {"status": "subscribed"}
    except IntegrityError:
        await db.rollback()
        return {"status": "already_subscribed"}


async def unsubscribe_from_course(db: AsyncSession, user_id: UUID, course_id: UUID) -> dict:
    sub = await db.scalar(
        select(CourseSubscription).where(
            CourseSubscription.user_id == user_id,
            CourseSubscription.course_id == course_id,
        )
    )
    if not sub:
        return {"status": "not_subscribed"}

    await db.delete(sub)
    await db.commit()
    return {"status": "unsubscribed"}


async def is_subscribed(db: AsyncSession, user_id: UUID, course_id: UUID) -> bool:
    sub = await db.scalar(
        select(CourseSubscription).where(
            CourseSubscription.user_id == user_id,
            CourseSubscription.course_id == course_id,
        )
    )
    return sub is not None
