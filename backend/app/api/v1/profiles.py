from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.database import get_db
from app.models.domain import User
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services.profiles import get_or_create_profile, profile_response, update_profile

router = APIRouter(prefix="/profile", tags=["profiles"])


@router.get("/me", response_model=ProfileResponse)
def read_my_profile(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return profile_response(get_or_create_profile(db, user), user)


@router.put("/me", response_model=ProfileResponse)
def write_my_profile(body: ProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return profile_response(update_profile(db, user, body), user)
