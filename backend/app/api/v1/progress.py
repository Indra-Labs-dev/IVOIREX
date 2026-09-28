from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.database import get_db
from app.models.domain import User
from app.schemas.campus import CompleteLessonRequest, LessonCompletionResponse
from app.services.campus import complete_lesson

router = APIRouter(prefix="/progress", tags=["campus-progress"])


@router.post("/complete", response_model=LessonCompletionResponse)
def complete(body: CompleteLessonRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return complete_lesson(db, user, str(body.lesson_id))
