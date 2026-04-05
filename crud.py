from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
import models
import schemas

# crud курсов

async def create_course(db: AsyncSession, course: schemas.CourseCreate):
    db_course = models.Course(**course.model_dump())
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course

async def get_courses(
    db: AsyncSession,
    category: Optional[str] = None,
    level: Optional[models.CourseLevel] = None,
    is_published: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    limit: int = 10,
    offset: int = 0
):
    query = select(models.Course)

    # filter
    if category:
        query = query.where(models.Course.category == category)
    if level:
        query = query.where(models.Course.level == level)
    if is_published is not None:
        query = query.where(models.Course.is_published == is_published)
    if search:
        query = query.where(models.Course.title.ilike(f"%{search}%"))

    # sort
    sort_column = getattr(models.Course, sort_by, models.Course.created_at)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()
    
    query = query.order_by(sort_column)

    # пагинация(сдвиг)
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_course_by_id(db: AsyncSession, course_id: int):
    result = await db.execute(select(models.Course).where(models.Course.id == course_id))
    return result.scalar_one_or_none()

async def update_course(db: AsyncSession, course_id: int, course_update: schemas.CourseUpdate):
    db_course = await get_course_by_id(db, course_id)
    if not db_course:
        return None
    
    # обновляем онли переданные поля
    update_data = course_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_course, key, value)
        
    await db.commit()
    await db.refresh(db_course)
    return db_course

async def delete_course(db: AsyncSession, course_id: int):
    db_course = await get_course_by_id(db, course_id)
    if db_course:
        await db.delete(db_course)
        await db.commit()
        return True
    return False

# crud уроков

async def create_lesson(db: AsyncSession, lesson: schemas.LessonCreate):
    db_lesson = models.Lesson(**lesson.model_dump())
    db.add(db_lesson)
    await db.commit()
    await db.refresh(db_lesson)
    return db_lesson

async def get_lessons_by_course(db: AsyncSession, course_id: int):
    result = await db.execute(select(models.Lesson).where(models.Lesson.course_id == course_id).order_by(models.Lesson.position))
    return result.scalars().all()

async def get_lesson_by_id(db: AsyncSession, lesson_id: int):
    result = await db.execute(select(models.Lesson).where(models.Lesson.id == lesson_id))
    return result.scalar_one_or_none()

async def update_lesson(db: AsyncSession, lesson_id: int, lesson_update: schemas.LessonUpdate):
    db_lesson = await get_lesson_by_id(db, lesson_id)
    if not db_lesson:
        return None
        
    # обновляем онли переданные поля
    update_data = lesson_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lesson, key, value)
        
    await db.commit()
    await db.refresh(db_lesson)
    return db_lesson

async def delete_lesson(db: AsyncSession, lesson_id: int):
    db_lesson = await get_lesson_by_id(db, lesson_id)
    if db_lesson:
        await db.delete(db_lesson)
        await db.commit()
        return True
    return False