from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field


CourseLevel = Literal["Débutant", "Intermédiaire", "Avancé"]
CourseStatus = Literal["DRAFT", "PUBLISHED", "ARCHIVED"]
LessonType = Literal["ARTICLE", "VIDEO", "RESOURCE"]
EnrollmentStatus = Literal["ACTIVE", "COMPLETED", "CANCELLED"]


class LessonOutline(BaseModel):
    id: UUID
    title: str
    slug: str
    content_type: LessonType
    duration_minutes: int
    position: int


class ModuleOutline(BaseModel):
    id: UUID
    title: str
    slug: str
    position: int
    lessons: list[LessonOutline]


class CourseCard(BaseModel):
    id: UUID
    title: str
    slug: str
    short_description: str
    thumbnail: str | None
    category: str
    level: CourseLevel
    duration_minutes: int
    language: str
    instructor: str
    is_demo: bool
    module_count: int
    lesson_count: int


class CoursePage(BaseModel):
    items: list[CourseCard]
    total: int
    page: int
    page_size: int
    has_more: bool
    categories: list[str]
    levels: list[str]


class CourseDetail(CourseCard):
    description: str
    status: CourseStatus
    published_at: datetime
    modules: list[ModuleOutline]


class CourseEnrollmentRequest(BaseModel):
    course_id: UUID


class EnrollmentCreated(BaseModel):
    id: UUID
    course_id: UUID
    status: EnrollmentStatus
    enrolled_at: datetime


class EnrollmentItem(BaseModel):
    id: UUID
    course_id: UUID
    course_slug: str
    course_title: str
    category: str
    level: CourseLevel
    status: EnrollmentStatus
    enrolled_at: datetime
    completed_at: datetime | None
    completed_lessons: int
    total_lessons: int
    progress_percent: int


class EnrollmentPage(BaseModel):
    items: list[EnrollmentItem]
    total: int
    limit: int
    offset: int
    has_more: bool


class LessonContent(BaseModel):
    id: UUID
    course_id: UUID
    course_slug: str
    course_title: str
    module_id: UUID
    module_title: str
    title: str
    slug: str
    content: str
    content_type: LessonType
    duration_minutes: int
    position: int
    is_completed: bool


class CompleteLessonRequest(BaseModel):
    lesson_id: UUID


class CourseProgress(BaseModel):
    enrollment_status: EnrollmentStatus
    completed_at: datetime | None
    completed_lessons: int
    total_lessons: int
    progress_percent: int


class LessonCompletionResponse(BaseModel):
    lesson_id: UUID
    completed_at: datetime
    already_completed: bool
    course_progress: CourseProgress
