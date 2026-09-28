"""Exercises Campus constraints, relations and API persistence on PostgreSQL."""
import uuid
import os
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.domain import Course, CourseModule, Enrollment, Lesson, LessonProgress, User
from app.security.tokens import issue_token
from datetime import timedelta


@pytest.mark.integration
@pytest.mark.skipif(os.getenv("RUN_POSTGRES_INTEGRATION") != "1", reason="Use the isolated PostgreSQL integration profile")
def test_postgres_enrollment_lesson_progress_round_trip():
    suffix = uuid.uuid4().hex[:12]
    user = User(email=f"campus-{suffix}@test.invalid", username=f"campus_{suffix}", password_hash="not-a-login")
    course = Course(
        title="Cours PostgreSQL", slug=f"pg-test-{suffix}", short_description="Cours de test intégré",
        description="Contenu contrôlé par le test PostgreSQL.", category="Test", level="Débutant",
        duration_minutes=10, language="fr", instructor="Test", status="PUBLISHED",
        published_at=datetime.now(timezone.utc), is_demo=False,
    )
    module = CourseModule(course=course, title="Module", slug="module", position=0)
    module.lessons = [
        Lesson(title="Leçon 1", slug="lecon-1", content="Contenu persistant.", content_type="ARTICLE", duration_minutes=5, position=0),
        Lesson(title="Leçon 2", slug="lecon-2", content="Suite persistante.", content_type="ARTICLE", duration_minutes=5, position=1),
    ]
    with SessionLocal() as db:
        db.add_all([user, course])
        db.commit()
        db.refresh(user)
        db.refresh(course)
        lesson_ids = [lesson.id for lesson in db.query(Lesson).join(CourseModule).filter(CourseModule.course_id == course.id).order_by(Lesson.position).all()]
        token = issue_token(user.id, "access", timedelta(minutes=10), user.token_version)
    try:
        with TestClient(app) as client:
            assert client.get("/api/v1/courses/" + course.slug).status_code == 200
            assert client.get("/api/v1/lessons/" + lesson_ids[0], headers={"Authorization": f"Bearer {token}"}).status_code == 403
            enrolled = client.post("/api/v1/enrollments", json={"course_id": course.id}, headers={"Authorization": f"Bearer {token}"})
            assert enrolled.status_code == 201, enrolled.text
            assert client.post("/api/v1/enrollments", json={"course_id": course.id}, headers={"Authorization": f"Bearer {token}"}).status_code == 409
            opened = client.get("/api/v1/lessons/" + lesson_ids[0], headers={"Authorization": f"Bearer {token}"})
            assert opened.status_code == 200 and opened.json()["content"] == "Contenu persistant."
            progress = client.post("/api/v1/progress/complete", json={"lesson_id": lesson_ids[0]}, headers={"Authorization": f"Bearer {token}"})
            assert progress.status_code == 200 and progress.json()["course_progress"]["progress_percent"] == 50
            assert client.post("/api/v1/progress/complete", json={"lesson_id": lesson_ids[1]}, headers={"Authorization": f"Bearer {token}"}).json()["course_progress"]["enrollment_status"] == "COMPLETED"
            mine = client.get("/api/v1/enrollments/me", headers={"Authorization": f"Bearer {token}"})
            assert mine.status_code == 200 and mine.json()["items"][0]["progress_percent"] == 100
        with SessionLocal() as db:
            assert db.query(LessonProgress).filter(LessonProgress.user_id == user.id).count() == 2
            assert db.query(Enrollment).filter(Enrollment.user_id == user.id, Enrollment.status == "COMPLETED").count() == 1
    finally:
        with SessionLocal() as db:
            db.query(User).filter(User.id == user.id).delete()
            db.query(Course).filter(Course.id == course.id).delete()
            db.commit()
