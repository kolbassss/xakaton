from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from models import CourseLevel

# lessons
class LessonBase(BaseModel):
    title: str
    summary: str
    position: int
    duration_minutes: int = Field(..., gt=0)
    is_open: bool

class LessonCreate(LessonBase):
    course_id: int

class LessonResponse(LessonBase):
    id: int
    course_id: int

    class Config:
        from_attributes = True
        
class LessonUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    position: Optional[int] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    is_open: Optional[bool] = None


# курсы
class CourseBase(BaseModel):
    title: str
    description: str
    category: str
    level: CourseLevel
    is_published: bool

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    level: Optional[CourseLevel] = None
    is_published: Optional[bool] = None

# статы
class CourseStats(BaseModel):
    total_lessons: int
    total_duration_minutes: int

class CourseDetailsResponse(BaseModel):
    course: CourseResponse
    stats: CourseStats
    lessons: List[LessonResponse]



