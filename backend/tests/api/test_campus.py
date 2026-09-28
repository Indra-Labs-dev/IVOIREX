from datetime import datetime, timezone
from app.models.domain import Course, CourseModule, Lesson


def register(client, username="campus_learner"):
    response = client.post("/api/v1/auth/register", json={
        "email": f"{username}@example.ci",
        "username": username,
        "password": "safe-campus-passphrase-123",
    })
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_course(database, *, slug="python-demo", status="PUBLISHED", modules_count=1, lessons_per_module=2):
    with database() as db:
        course = Course(
            title="Python de démonstration",
            slug=slug,
            short_description="Apprendre les bases de Python avec un exercice guidé.",
            description="Un cours de test article, stocké dans la base.",
            category="Programmation",
            level="Débutant",
            duration_minutes=20,
            language="fr",
            instructor="Équipe de démonstration",
            status=status,
            is_demo=True,
            published_at=datetime.now(timezone.utc) if status == "PUBLISHED" else None,
        )
        db.add(course)
        db.flush()
        lesson_ids = []
        for module_position in range(modules_count):
            module = CourseModule(course_id=course.id, title=f"Module {module_position + 1}", slug=f"module-{module_position + 1}", position=module_position)
            db.add(module)
            db.flush()
            for lesson_position in range(lessons_per_module):
                lesson = Lesson(
                    module_id=module.id,
                    title=f"Leçon {module_position + 1}.{lesson_position + 1}",
                    slug=f"lecon-{module_position + 1}-{lesson_position + 1}",
                    content="Contenu pédagogique persistant pour cette leçon.",
                    content_type="ARTICLE",
                    duration_minutes=10,
                    position=lesson_position,
                )
                db.add(lesson)
                db.flush()
                lesson_ids.append(lesson.id)
        db.commit()
        return course.id, lesson_ids


def test_catalog_only_lists_published_courses_and_paginates(client, database):
    create_course(database, slug="python-premier")
    create_course(database, slug="python-second")
    create_course(database, slug="python-brouillon", status="DRAFT")

    page = client.get("/api/v1/courses?page=1&page_size=1&q=Python&category=Programmation&level=Débutant")
    assert page.status_code == 200
    body = page.json()
    assert body["total"] == 2
    assert len(body["items"]) == 1
    assert body["has_more"] is True
    assert body["items"][0]["is_demo"] is True
    assert body["items"][0]["lesson_count"] == 2
    assert client.get("/api/v1/courses?page_size=25").status_code == 422


def test_course_detail_shows_outline_but_draft_stays_hidden(client, database):
    create_course(database, slug="cours-visible", modules_count=2, lessons_per_module=2)
    create_course(database, slug="cours-cache", status="DRAFT")

    detail = client.get("/api/v1/courses/cours-visible")
    assert detail.status_code == 200
    assert detail.json()["module_count"] == 2
    assert detail.json()["lesson_count"] == 4
    assert "content" not in detail.json()["modules"][0]["lessons"][0]
    assert client.get("/api/v1/courses/cours-cache").status_code == 404
    assert client.get("/api/v1/courses/invalid--slug").status_code == 422


def test_enrollment_is_authenticated_unique_and_required_for_lesson_access(client, database):
    course_id, lesson_ids = create_course(database)
    body = {"course_id": course_id}
    assert client.post("/api/v1/enrollments", json=body).status_code == 401
    first_headers = register(client)
    enrollment = client.post("/api/v1/enrollments", headers=first_headers, json=body)
    assert enrollment.status_code == 201
    assert enrollment.json()["status"] == "ACTIVE"
    assert client.post("/api/v1/enrollments", headers=first_headers, json=body).status_code == 409
    assert client.get(f"/api/v1/lessons/{lesson_ids[0]}", headers=first_headers).status_code == 200

    second_headers = register(client, "campus_other")
    assert client.get(f"/api/v1/lessons/{lesson_ids[0]}", headers=second_headers).status_code == 403
    assert client.post("/api/v1/progress/complete", headers=second_headers, json={"lesson_id": lesson_ids[0]}).status_code == 403


def test_progress_is_persisted_idempotent_and_completes_course(client, database):
    course_id, lesson_ids = create_course(database, modules_count=1, lessons_per_module=2)
    headers = register(client, "campus_progress")
    assert client.post("/api/v1/enrollments", headers=headers, json={"course_id": course_id}).status_code == 201

    opened = client.get(f"/api/v1/lessons/{lesson_ids[0]}", headers=headers)
    assert opened.status_code == 200
    assert opened.json()["is_completed"] is False
    assert opened.json()["content"] == "Contenu pédagogique persistant pour cette leçon."

    first = client.post("/api/v1/progress/complete", headers=headers, json={"lesson_id": lesson_ids[0]})
    assert first.status_code == 200
    assert first.json()["course_progress"]["completed_lessons"] == 1
    assert first.json()["course_progress"]["total_lessons"] == 2
    assert first.json()["course_progress"]["progress_percent"] == 50
    repeated = client.post("/api/v1/progress/complete", headers=headers, json={"lesson_id": lesson_ids[0]})
    assert repeated.json()["already_completed"] is True
    assert repeated.json()["course_progress"]["completed_lessons"] == 1

    last = client.post("/api/v1/progress/complete", headers=headers, json={"lesson_id": lesson_ids[1]})
    assert last.status_code == 200
    assert last.json()["course_progress"]["progress_percent"] == 100
    assert last.json()["course_progress"]["enrollment_status"] == "COMPLETED"
    assert last.json()["course_progress"]["completed_at"] is not None
    assert client.get(f"/api/v1/lessons/{lesson_ids[0]}", headers=headers).json()["is_completed"] is True

    enrollment_list = client.get("/api/v1/enrollments/me", headers=headers).json()
    assert enrollment_list["items"][0]["completed_lessons"] == 2
    assert enrollment_list["items"][0]["progress_percent"] == 100

