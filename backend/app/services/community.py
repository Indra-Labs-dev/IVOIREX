from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.domain import CommunityComment, CommunityPost, CommunityReaction, User
from app.schemas.community import (
    CommunityCommentCreate, CommunityCommentResponse, CommunityPostCard,
    CommunityPostCreate, CommunityPostDetail, CommunityPostPage,
    CommunityReactionResult,
)


def _counts(post_id):
    comments = select(func.count(CommunityComment.id)).where(CommunityComment.post_id == post_id).scalar_subquery()
    reactions = select(func.count(CommunityReaction.user_id)).where(CommunityReaction.post_id == post_id).scalar_subquery()
    return comments, reactions


def _post_card(post, username, comment_count, reaction_count, viewer_reacted):
    return CommunityPostCard(
        id=post.id, user_id=post.user_id, username=username,
        title=post.title, excerpt=post.content[:240], created_at=post.created_at,
        comment_count=comment_count, reaction_count=reaction_count,
        viewer_reacted=bool(viewer_reacted),
    )


def list_posts(db: Session, viewer: User | None, page: int, page_size: int) -> CommunityPostPage:
    total = db.scalar(select(func.count(CommunityPost.id))) or 0
    comment_count, reaction_count = _counts(CommunityPost.id)
    reacted = select(CommunityReaction.post_id).where(
        CommunityReaction.post_id == CommunityPost.id,
        CommunityReaction.user_id == (viewer.id if viewer else ""),
    ).exists()
    rows = db.execute(
        select(CommunityPost, User.username, comment_count, reaction_count, reacted)
        .join(User, User.id == CommunityPost.user_id)
        .order_by(CommunityPost.created_at.desc(), CommunityPost.id.desc())
        .offset((page - 1) * page_size).limit(page_size)
    ).all()
    return CommunityPostPage(
        items=[_post_card(*row) for row in rows], total=total, page=page,
        page_size=page_size, has_more=page * page_size < total,
    )


def get_post(db: Session, post_id: str, viewer: User | None) -> CommunityPostDetail:
    comment_count, reaction_count = _counts(CommunityPost.id)
    reacted = select(CommunityReaction.post_id).where(
        CommunityReaction.post_id == CommunityPost.id,
        CommunityReaction.user_id == (viewer.id if viewer else ""),
    ).exists()
    row = db.execute(
        select(CommunityPost, User.username, comment_count, reaction_count, reacted)
        .join(User, User.id == CommunityPost.user_id)
        .where(CommunityPost.id == post_id)
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = db.execute(
        select(CommunityComment, User.username)
        .join(User, User.id == CommunityComment.user_id)
        .where(CommunityComment.post_id == post_id)
        .order_by(CommunityComment.created_at, CommunityComment.id)
    ).all()
    return CommunityPostDetail(
        **_post_card(*row).model_dump(), content=row[0].content,
        comments=[CommunityCommentResponse(
            id=comment.id, user_id=comment.user_id, username=username,
            content=comment.content, created_at=comment.created_at,
        ) for comment, username in comments],
    )


def create_post(db: Session, user: User, body: CommunityPostCreate) -> CommunityPostDetail:
    post = CommunityPost(user_id=user.id, title=body.title.strip(), content=body.content.strip())
    if not post.title or not post.content:
        raise HTTPException(status_code=422, detail="Title and content cannot be blank")
    db.add(post)
    db.commit()
    db.refresh(post)
    return get_post(db, post.id, user)


def create_comment(db: Session, user: User, post_id: str, body: CommunityCommentCreate) -> CommunityPostDetail:
    if db.get(CommunityPost, post_id) is None:
        raise HTTPException(status_code=404, detail="Post not found")
    content = body.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="Comment cannot be blank")
    db.add(CommunityComment(post_id=post_id, user_id=user.id, content=content))
    db.commit()
    return get_post(db, post_id, user)


def set_reaction(db: Session, user: User, post_id: str, reacted: bool) -> CommunityReactionResult:
    if db.get(CommunityPost, post_id) is None:
        raise HTTPException(status_code=404, detail="Post not found")
    key = (post_id, user.id)
    existing = db.get(CommunityReaction, key)
    if reacted and existing is None:
        db.add(CommunityReaction(post_id=post_id, user_id=user.id))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
    elif not reacted and existing is not None:
        db.delete(existing)
        db.commit()
    count = db.scalar(select(func.count(CommunityReaction.user_id)).where(CommunityReaction.post_id == post_id)) or 0
    return CommunityReactionResult(reacted=reacted, reaction_count=count)
