from datetime import datetime
from pydantic import BaseModel, Field, field_validator


def normalize_tags(values: list[str]) -> list[str]:
    cleaned = [" ".join(value.split()) for value in values]
    return list(dict.fromkeys(value for value in cleaned if value))


class ProfileUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=80)
    bio: str = Field(default="", max_length=280)
    city: str = Field(min_length=1, max_length=64)
    country: str = Field(min_length=1, max_length=64)
    skills: list[str] = Field(default_factory=list, max_length=12)
    interests: list[str] = Field(default_factory=list, max_length=12)

    @field_validator("display_name", "city", "country", mode="before")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("bio", mode="before")
    @classmethod
    def trim_bio(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("skills", "interests")
    @classmethod
    def clean_tags(cls, values: list[str]) -> list[str]:
        cleaned = normalize_tags(values)
        if any(len(value) > 40 for value in cleaned):
            raise ValueError("Each item must be 40 characters or fewer")
        return cleaned


class ProfileResponse(ProfileUpdate):
    user_id: str
    username: str
    updated_at: datetime
