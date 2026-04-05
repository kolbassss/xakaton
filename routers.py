from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

import crud
import schemas
import models
from database import get_db

router = APIRouter()

# курсы

@router.post("/courses/", response_model=schemas.CourseResponse, tags=["Courses"])
async def create_course(course: schemas.CourseCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_course(db=db, course=course)

@router.get("/courses/", response_model=List[schemas.CourseResponse], tags=["Courses"])
async def read_courses(
    category: Optional[str] = Query(None, description="категория"),
    level: Optional[models.CourseLevel] = Query(None, description="уровень"),
    is_published: Optional[bool] = Query(None, description="статус"),
    search: Optional[str] = Query(None, description="поиск"),
    sort_by: str = Query("created_at", description="сортировать по"),
    sort_order: str = Query("desc", description="порядок"),
    limit: int = Query(10, ge=1, le=100, description="лимит"),
    offset: int = Query(0, ge=0, description="сдвиг"),
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_courses(
        db, category, level, is_published, search, sort_by, sort_order, limit, offset
    )


@router.get("/courses/{course_id}/details", response_model=schemas.CourseDetailsResponse, tags=["Courses"])
async def read_course_details(course_id: int, db: AsyncSession = Depends(get_db)):
    course = await crud.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    lessons = await crud.get_lessons_by_course(db, course_id)
    
    # статы
    total_lessons = len(lessons)
    total_duration = sum(lesson.duration_minutes for lesson in lessons)
    
    return schemas.CourseDetailsResponse(
        course=course,
        stats=schemas.CourseStats(
            total_lessons=total_lessons,
            total_duration_minutes=total_duration
        ),
        lessons=lessons
    )

@router.put("/courses/{course_id}", response_model=schemas.CourseResponse, tags=["Courses"])
async def update_course(course_id: int, course_update: schemas.CourseUpdate, db: AsyncSession = Depends(get_db)):
    updated_course = await crud.update_course(db, course_id, course_update)
    if not updated_course:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated_course

@router.delete("/courses/{course_id}", tags=["Courses"])
async def delete_course(course_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_course(db, course_id)
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"detail": "course deleted"}

# уроки

@router.post("/lessons/", response_model=schemas.LessonResponse, tags=["Lessons"])
async def create_lesson(lesson: schemas.LessonCreate, db: AsyncSession = Depends(get_db)):
    # проверка существования курса
    course = await crud.get_course_by_id(db, lesson.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return await crud.create_lesson(db=db, lesson=lesson)

@router.put("/lessons/{lesson_id}", response_model=schemas.LessonResponse, tags=["Lessons"])
async def update_lesson(lesson_id: int, lesson_update: schemas.LessonUpdate, db: AsyncSession = Depends(get_db)):
    updated_lesson = await crud.update_lesson(db, lesson_id, lesson_update)
    if not updated_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return updated_lesson

@router.delete("/lessons/{lesson_id}", tags=["Lessons"])
async def delete_lesson(lesson_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_lesson(db, lesson_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {"detail": "lesson deleted"}