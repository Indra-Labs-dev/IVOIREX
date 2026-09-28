from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, Response
from sqlalchemy.orm import Session

from app.api.deps import current_user, optional_current_user
from app.core.database import get_db
from app.models.domain import User
from app.schemas.community import (
    CommunityCommentCreate, CommunityPostCreate, CommunityPostDetail,
    CommunityPostPage, CommunityReactionResult,
)
from app.services.community import create_comment, create_post, get_post, list_posts, set_reaction

router = APIRouter(prefix="/community/posts", tags=["community"])


@router.get("", response_model=CommunityPostPage)
def posts(
    page: Annotated[int, Query(ge=1, le=100_000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=30)] = 15,
    viewer: User | None = Depends(optional_current_user),
    db: Session = Depends(get_db),
):
    return list_posts(db, viewer, page, page_size)


@router.post("", response_model=CommunityPostDetail, status_code=201)
def new_post(body: CommunityPostCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return create_post(db, user, body)


@router.get("/{post_id}", response_model=CommunityPostDetail)
def post_detail(
    post_id: Annotated[UUID, Path()],
    viewer: User | None = Depends(optional_current_user),
    db: Session = Depends(get_db),
):
    return get_post(db, str(post_id), viewer)


@router.post("/{post_id}/comments", response_model=CommunityPostDetail)
def comment(
    post_id: Annotated[UUID, Path()],
    body: CommunityCommentCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return create_comment(db, user, str(post_id), body)


@router.put("/{post_id}/reaction", response_model=CommunityReactionResult)
def react(
    post_id: Annotated[UUID, Path()],
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return set_reaction(db, user, str(post_id), True)


@router.delete("/{post_id}/reaction", response_model=CommunityReactionResult)
def unreact(
    post_id: Annotated[UUID, Path()],
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return set_reaction(db, user, str(post_id), False)
