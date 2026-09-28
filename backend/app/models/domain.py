import uuid
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

def utcnow() -> datetime:
    return datetime.now(timezone.utc)
class User(Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_email", "email", unique=True), Index("ix_users_username", "username", unique=True))
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(32), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str] = mapped_column(Text, nullable=False, default="")
    city: Mapped[str] = mapped_column(String(64), nullable=False, default="Abidjan")
    skills: Mapped[str] = mapped_column(Text, nullable=False, default="")
    xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    streak: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    reputation: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="USER", server_default="USER")
    token_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default="now()")

class Profile(Base):
    __tablename__ = "profiles"
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(80), nullable=False)
    bio: Mapped[str] = mapped_column(String(280), nullable=False, default="")
    city: Mapped[str] = mapped_column(String(64), nullable=False, default="Abidjan")
    country: Mapped[str] = mapped_column(String(64), nullable=False, default="Côte d’Ivoire")
    skills: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    interests: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow, server_default="now()")


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')", name="ck_courses_status"),
        CheckConstraint("duration_minutes > 0", name="ck_courses_duration_positive"),
        CheckConstraint("status != 'PUBLISHED' OR published_at IS NOT NULL", name="ck_courses_published_at"),
        Index("ix_courses_catalog", "status", "published_at"),
        Index("ix_courses_category_level", "category", "level"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    short_description: Mapped[str] = mapped_column(String(280), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String(12), nullable=False, default="fr", server_default="fr")
    instructor: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="DRAFT", server_default="DRAFT")
    is_demo: Mapped[bool] = mapped_column(nullable=False, default=False, server_default="false")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow, server_default="now()")
    modules: Mapped[list["CourseModule"]] = relationship(back_populates="course", cascade="all, delete-orphan", order_by="CourseModule.position")


class CourseModule(Base):
    __tablename__ = "course_modules"
    __table_args__ = (
        UniqueConstraint("course_id", "slug", name="uq_course_modules_course_slug"),
        UniqueConstraint("course_id", "position", name="uq_course_modules_course_position"),
        CheckConstraint("position >= 0", name="ck_course_modules_position_nonnegative"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id: Mapped[str] = mapped_column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    course: Mapped[Course] = relationship(back_populates="modules")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="module", cascade="all, delete-orphan", order_by="Lesson.position")


class Lesson(Base):
    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("module_id", "slug", name="uq_lessons_module_slug"),
        UniqueConstraint("module_id", "position", name="uq_lessons_module_position"),
        CheckConstraint("content_type IN ('ARTICLE', 'VIDEO', 'RESOURCE')", name="ck_lessons_content_type"),
        CheckConstraint("duration_minutes >= 0", name="ck_lessons_duration_nonnegative"),
        CheckConstraint("position >= 0", name="ck_lessons_position_nonnegative"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    module_id: Mapped[str] = mapped_column(String(36), ForeignKey("course_modules.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(16), nullable=False, default="ARTICLE", server_default="ARTICLE")
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=5, server_default="5")
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    module: Mapped[CourseModule] = relationship(back_populates="lessons")


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_enrollments_user_course"),
        CheckConstraint("status IN ('ACTIVE', 'COMPLETED', 'CANCELLED')", name="ck_enrollments_status"),
        Index("ix_enrollments_user_enrolled", "user_id", "enrolled_at"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[str] = mapped_column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="ACTIVE", server_default="ACTIVE")
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default="now()")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    course: Mapped[Course] = relationship()


class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (Index("ix_lesson_progress_lesson", "lesson_id"),)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    lesson_id: Mapped[str] = mapped_column(String(36), ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default="now()")


class CommunityPost(Base):
    __tablename__ = "community_posts"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="ck_community_posts_title_nonempty"),
        CheckConstraint("length(trim(content)) > 0", name="ck_community_posts_content_nonempty"),
        Index("ix_community_posts_created", "created_at", "id"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow, server_default="now()")
    comments: Mapped[list["CommunityComment"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    reactions: Mapped[list["CommunityReaction"]] = relationship(back_populates="post", cascade="all, delete-orphan")


class CommunityComment(Base):
    __tablename__ = "community_comments"
    __table_args__ = (
        CheckConstraint("length(trim(content)) > 0", name="ck_community_comments_content_nonempty"),
        Index("ix_community_comments_post_created", "post_id", "created_at"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id: Mapped[str] = mapped_column(String(36), ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default="now()")
    post: Mapped[CommunityPost] = relationship(back_populates="comments")


class CommunityReaction(Base):
    __tablename__ = "community_reactions"
    post_id: Mapped[str] = mapped_column(String(36), ForeignKey("community_posts.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow, server_default="now()")
    post: Mapped[CommunityPost] = relationship(back_populates="reactions")
