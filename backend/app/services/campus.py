from datetime import datetime, timezone
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload
from fastapi import HTTPException
from app.models.domain import Course, CourseModule, Enrollment, Lesson, LessonProgress, User
from app.schemas.campus import (
    CourseCard, CourseDetail, CoursePage, EnrollmentCreated, EnrollmentItem,
    EnrollmentPage, LessonContent, LessonCompletionResponse, CourseProgress,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _course_counts(course_id: str):
    module_count = select(func.count(CourseModule.id)).where(CourseModule.course_id == course_id).scalar_subquery()
    lesson_count = (
        select(func.count(Lesson.id))
        .join(CourseModule, Lesson.module_id == CourseModule.id)
        .where(CourseModule.course_id == course_id)
        .scalar_subquery()
    )
    return module_count, lesson_count


def _course_card(course: Course, module_count: int, lesson_count: int) -> CourseCard:
    return CourseCard(
        id=course.id,
        title=course.title,
        slug=course.slug,
        short_description=course.short_description,
        thumbnail=course.thumbnail,
        category=course.category,
        level=course.level,
        duration_minutes=course.duration_minutes,
        language=course.language,
        instructor=course.instructor,
        is_demo=course.is_demo,
        module_count=module_count,
        lesson_count=lesson_count,
    )


def list_courses(
    db: Session,
    *,
    page: int,
    page_size: int,
    q: str | None,
    category: str | None,
    level: str | None,
    max_duration_minutes: int | None,
) -> CoursePage:
    filters = [Course.status == "PUBLISHED"]
    if q and (query := q.strip()):
        pattern = f"%{query}%"
        filters.append(or_(Course.title.ilike(pattern), Course.short_description.ilike(pattern), Course.description.ilike(pattern)))
    if category:
        filters.append(Course.category == category)
    if level:
        filters.append(Course.level == level)
    if max_duration_minutes is not None:
        filters.append(Course.duration_minutes <= max_duration_minutes)

    total = db.scalar(select(func.count(Course.id)).where(*filters)) or 0
    module_count, lesson_count = _course_counts(Course.id)
    rows = db.execute(
        select(Course, module_count.label("module_count"), lesson_count.label("lesson_count"))
        .where(*filters)
        .order_by(Course.published_at.desc(), Course.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    categories = list(db.scalars(
        select(Course.category).where(Course.status == "PUBLISHED").distinct().order_by(Course.category)
    ))
    levels = list(db.scalars(
        select(Course.level).where(Course.status == "PUBLISHED").distinct().order_by(Course.level)
    ))
    return CoursePage(
        items=[_course_card(course, modules, lessons) for course, modules, lessons in rows],
        total=total,
        page=page,
        page_size=page_size,
        has_more=(page * page_size) < total,
        categories=categories,
        levels=levels,
    )


def get_course(db: Session, slug: str) -> CourseDetail:
    course = db.scalar(
        select(Course)
        .options(selectinload(Course.modules).selectinload(CourseModule.lessons))
        .where(Course.slug == slug, Course.status == "PUBLISHED")
    )
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    modules = [
        {
            "id": module.id,
            "title": module.title,
            "slug": module.slug,
            "position": module.position,
            "lessons": [
                {
                    "id": lesson.id,
                    "title": lesson.title,
                    "slug": lesson.slug,
                    "content_type": lesson.content_type,
                    "duration_minutes": lesson.duration_minutes,
                    "position": lesson.position,
                }
                for lesson in module.lessons
            ],
        }
        for module in course.modules
    ]
    return CourseDetail(
        **_course_card(course, len(course.modules), sum(len(module.lessons) for module in course.modules)).model_dump(),
        description=course.description,
        status=course.status,
        published_at=course.published_at,
        modules=modules,
    )


def enroll(db: Session, user: User, course_id: str) -> EnrollmentCreated:
    course = db.scalar(select(Course).where(Course.id == course_id, Course.status == "PUBLISHED"))
    if course is None:
        raise HTTPException(status_code=404, detail="Published course not found")
    existing = db.scalar(select(Enrollment).where(Enrollment.user_id == user.id, Enrollment.course_id == course.id))
    if existing:
        raise HTTPException(status_code=409, detail="Already enrolled in this course")
    enrollment = Enrollment(user_id=user.id, course_id=course.id, status="ACTIVE")
    db.add(enrollment)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Already enrolled in this course") from exc
    db.refresh(enrollment)
    return EnrollmentCreated(id=enrollment.id, course_id=enrollment.course_id, status=enrollment.status, enrolled_at=enrollment.enrolled_at)


def list_enrollments(db: Session, user: User, limit: int, offset: int) -> EnrollmentPage:
    total = db.scalar(select(func.count(Enrollment.id)).where(Enrollment.user_id == user.id)) or 0
    total_lessons = (
        select(func.count(Lesson.id))
        .join(CourseModule, Lesson.module_id == CourseModule.id)
        .where(CourseModule.course_id == Enrollment.course_id)
        .correlate(Enrollment)
        .scalar_subquery()
    )
    completed_lessons = (
        select(func.count(LessonProgress.lesson_id))
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .join(CourseModule, Lesson.module_id == CourseModule.id)
        .where(LessonProgress.user_id == Enrollment.user_id, CourseModule.course_id == Enrollment.course_id)
        .correlate(Enrollment)
        .scalar_subquery()
    )
    rows = db.execute(
        select(Enrollment, Course, total_lessons.label("total_lessons"), completed_lessons.label("completed_lessons"))
        .join(Course, Enrollment.course_id == Course.id)
        .where(Enrollment.user_id == user.id)
        .order_by(Enrollment.enrolled_at.desc(), Enrollment.id)
        .offset(offset)
        .limit(limit)
    ).all()
    items = []
    for enrollment, course, total_count, completed_count in rows:
        percent = round((completed_count / total_count) * 100) if total_count else 0
        items.append(EnrollmentItem(
            id=enrollment.id,
            course_id=course.id,
            course_slug=course.slug,
            course_title=course.title,
            category=course.category,
            level=course.level,
            status=enrollment.status,
            enrolled_at=enrollment.enrolled_at,
            completed_at=enrollment.completed_at,
            completed_lessons=completed_count,
            total_lessons=total_count,
            progress_percent=percent,
        ))
    return EnrollmentPage(items=items, total=total, limit=limit, offset=offset, has_more=(offset + limit) < total)


def get_lesson(db: Session, user: User, lesson_id: str) -> LessonContent:
    lesson = db.scalar(
        select(Lesson)
        .options(joinedload(Lesson.module).joinedload(CourseModule.course))
        .where(Lesson.id == lesson_id)
    )
    if lesson is None or lesson.module.course.status != "PUBLISHED":
        raise HTTPException(status_code=404, detail="Lesson not found")
    course = lesson.module.course
    enrollment = db.scalar(select(Enrollment).where(
        Enrollment.user_id == user.id,
        Enrollment.course_id == course.id,
        Enrollment.status.in_(["ACTIVE", "COMPLETED"]),
    ))
    if enrollment is None:
        raise HTTPException(status_code=403, detail="Enroll in this course to open its lessons")
    completed = db.get(LessonProgress, (user.id, lesson.id)) is not None
    return LessonContent(
        id=lesson.id,
        course_id=course.id,
        course_slug=course.slug,
        course_title=course.title,
        module_id=lesson.module.id,
        module_title=lesson.module.title,
        title=lesson.title,
        slug=lesson.slug,
        content=lesson.content,
        content_type=lesson.content_type,
        duration_minutes=lesson.duration_minutes,
        position=lesson.position,
        is_completed=completed,
    )


def complete_lesson(db: Session, user: User, lesson_id: str) -> LessonCompletionResponse:
    lesson = db.scalar(
        select(Lesson)
        .options(joinedload(Lesson.module).joinedload(CourseModule.course))
        .where(Lesson.id == lesson_id)
    )
    if lesson is None or lesson.module.course.status != "PUBLISHED":
        raise HTTPException(status_code=404, detail="Lesson not found")
    course = lesson.module.course
    enrollment = db.scalar(
        select(Enrollment)
        .where(Enrollment.user_id == user.id, Enrollment.course_id == course.id)
        .with_for_update()
    )
    if enrollment is None or enrollment.status == "CANCELLED":
        raise HTTPException(status_code=403, detail="An active enrollment is required")

    progress = db.get(LessonProgress, (user.id, lesson.id))
    already_completed = progress is not None
    if progress is None:
        progress = LessonProgress(user_id=user.id, lesson_id=lesson.id)
        db.add(progress)
        db.flush()

    total_count = db.scalar(
        select(func.count(Lesson.id))
        .join(CourseModule, Lesson.module_id == CourseModule.id)
        .where(CourseModule.course_id == course.id)
    ) or 0
    completed_count = db.scalar(
        select(func.count(LessonProgress.lesson_id))
        .join(Lesson, LessonProgress.lesson_id == Lesson.id)
        .join(CourseModule, Lesson.module_id == CourseModule.id)
        .where(LessonProgress.user_id == user.id, CourseModule.course_id == course.id)
    ) or 0
    if total_count > 0 and completed_count >= total_count and enrollment.status != "COMPLETED":
        enrollment.status = "COMPLETED"
        enrollment.completed_at = utcnow()
    db.commit()
    percent = round((completed_count / total_count) * 100) if total_count else 0
    return LessonCompletionResponse(
        lesson_id=lesson.id,
        completed_at=progress.completed_at,
        already_completed=already_completed,
        course_progress=CourseProgress(
            enrollment_status=enrollment.status,
            completed_at=enrollment.completed_at,
            completed_lessons=completed_count,
            total_lessons=total_count,
            progress_percent=percent,
        ),
    )
