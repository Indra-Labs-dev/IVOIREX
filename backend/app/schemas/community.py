from datetime import datetime
from pydantic import BaseModel, Field


class CommunityPostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=5000)


class CommunityCommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CommunityCommentResponse(BaseModel):
    id: str
    user_id: str
    username: str
    content: str
    created_at: datetime


class CommunityPostCard(BaseModel):
    id: str
    user_id: str
    username: str
    title: str
    excerpt: str
    created_at: datetime
    comment_count: int
    reaction_count: int
    viewer_reacted: bool


class CommunityPostDetail(CommunityPostCard):
    content: str
    comments: list[CommunityCommentResponse]


class CommunityPostPage(BaseModel):
    items: list[CommunityPostCard]
    total: int
    page: int
    page_size: int
    has_more: bool


class CommunityReactionResult(BaseModel):
    reacted: bool
    reaction_count: int
