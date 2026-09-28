from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.database import get_db
from app.models.domain import User
from app.schemas.campus import CourseEnrollmentRequest, EnrollmentCreated, EnrollmentPage
from app.services.campus import enroll, list_enrollments

router = APIRouter(prefix="/enrollments", tags=["campus-enrollments"])


@router.post("", status_code=201, response_model=EnrollmentCreated)
def create_enrollment(body: CourseEnrollmentRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return enroll(db, user, str(body.course_id))


@router.get("/me", response_model=EnrollmentPage)
def my_enrollments(
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    offset: Annotated[int, Query(ge=0, le=100_000)] = 0,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return list_enrollments(db, user, limit, offset)
