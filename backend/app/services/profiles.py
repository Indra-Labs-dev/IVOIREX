from sqlalchemy.orm import Session
from app.models.domain import Profile, User
from app.schemas.profile import ProfileResponse, ProfileUpdate


def get_or_create_profile(db: Session, user: User) -> Profile:
    profile = db.get(Profile, user.id)
    if profile is None:
        legacy_skills = [item.strip() for item in user.skills.split(",") if item.strip()]
        profile = Profile(
            user_id=user.id,
            display_name=user.username,
            bio=user.bio,
            city=user.city or "Abidjan",
            country="Côte d’Ivoire",
            skills=legacy_skills[:12],
            interests=[],
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def profile_response(profile: Profile, user: User) -> ProfileResponse:
    return ProfileResponse(
        user_id=user.id,
        username=user.username,
        display_name=profile.display_name,
        bio=profile.bio,
        city=profile.city,
        country=profile.country,
        skills=profile.skills,
        interests=profile.interests,
        updated_at=profile.updated_at,
    )


def update_profile(db: Session, user: User, body: ProfileUpdate) -> Profile:
    profile = get_or_create_profile(db, user)
    for field, value in body.model_dump().items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile
