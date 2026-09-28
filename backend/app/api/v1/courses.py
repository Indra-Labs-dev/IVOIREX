from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.campus import CourseDetail, CoursePage
from app.services.campus import get_course, list_courses

router = APIRouter(prefix="/courses", tags=["campus-courses"])


@router.get("", response_model=CoursePage)
def courses(
    page: Annotated[int, Query(ge=1, le=100_000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=24)] = 9,
    q: Annotated[str | None, Query(max_length=100)] = None,
    category: Annotated[str | None, Query(max_length=80)] = None,
    level: Annotated[str | None, Query(max_length=24)] = None,
    max_duration_minutes: Annotated[int | None, Query(ge=1, le=20_000)] = None,
    db: Session = Depends(get_db),
):
    return list_courses(db, page=page, page_size=page_size, q=q, category=category, level=level, max_duration_minutes=max_duration_minutes)


@router.get("/{slug}", response_model=CourseDetail)
def course_detail(
    slug: Annotated[str, Path(min_length=1, max_length=180, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")],
    db: Session = Depends(get_db),
):
    return get_course(db, slug)
