from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.database import get_db
from app.models.domain import User
from app.schemas.campus import LessonContent
from app.services.campus import get_lesson

router = APIRouter(prefix="/lessons", tags=["campus-lessons"])


@router.get("/{lesson_id}", response_model=LessonContent)
def lesson_content(
    lesson_id: Annotated[UUID, Path()],
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return get_lesson(db, user, str(lesson_id))
