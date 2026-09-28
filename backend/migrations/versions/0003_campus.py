"""Create the Campus catalog, lesson, enrollment, and completion tables."""
from alembic import op
from sqlalchemy import inspect
import sqlalchemy as sa

revision = "0003_campus"
down_revision = "0002_profiles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Older IVOIREX prototypes used `courses` and `enrollments` for a flat
    # XP-only catalog. Preserve those rows and their FK history under explicit
    # legacy names before introducing the relational Campus schema.
    inspector = inspect(op.get_bind())
    tables = set(inspector.get_table_names())
    if "courses" in tables and "status" not in {column["name"] for column in inspector.get_columns("courses")}:
        if "ivoirex_legacy_courses" in tables:
            raise RuntimeError("Both legacy and Campus course tables exist; manual schema review required")
        op.rename_table("courses", "ivoirex_legacy_courses")
        for index in inspect(op.get_bind()).get_indexes("ivoirex_legacy_courses"):
            name = index["name"]
            renamed = "legacy_" + name
            if len(renamed) > 63:
                renamed = "legacy_" + name[-55:]
            op.execute(sa.text(f'ALTER INDEX "{name}" RENAME TO "{renamed}"'))
    if "enrollments" in tables and "status" not in {column["name"] for column in inspector.get_columns("enrollments")}:
        if "ivoirex_legacy_enrollments" in tables:
            raise RuntimeError("Both legacy and Campus enrollment tables exist; manual schema review required")
        op.rename_table("enrollments", "ivoirex_legacy_enrollments")
        for index in inspect(op.get_bind()).get_indexes("ivoirex_legacy_enrollments"):
            name = index["name"]
            renamed = "legacy_" + name
            if len(renamed) > 63:
                renamed = "legacy_" + name[-55:]
            op.execute(sa.text(f'ALTER INDEX "{name}" RENAME TO "{renamed}"'))

    op.create_table(
        "courses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("slug", sa.String(180), nullable=False),
        sa.Column("short_description", sa.String(280), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("thumbnail", sa.String(500)),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("level", sa.String(24), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(12), server_default="fr", nullable=False),
        sa.Column("instructor", sa.String(120), nullable=False),
        sa.Column("status", sa.String(16), server_default="DRAFT", nullable=False),
        sa.Column("is_demo", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("status IN ('DRAFT', 'PUBLISHED', 'ARCHIVED')", name="ck_courses_status"),
        sa.CheckConstraint("duration_minutes > 0", name="ck_courses_duration_positive"),
        sa.CheckConstraint("status != 'PUBLISHED' OR published_at IS NOT NULL", name="ck_courses_published_at"),
    )
    op.create_index("ix_courses_slug", "courses", ["slug"], unique=True)
    op.create_index("ix_courses_catalog", "courses", ["status", "published_at"])
    op.create_index("ix_courses_category_level", "courses", ["category", "level"])
    op.create_index("ix_courses_category", "courses", ["category"])
    op.create_index("ix_courses_level", "courses", ["level"])

    op.create_table(
        "course_modules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("course_id", sa.String(36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("slug", sa.String(180), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("course_id", "slug", name="uq_course_modules_course_slug"),
        sa.UniqueConstraint("course_id", "position", name="uq_course_modules_course_position"),
        sa.CheckConstraint("position >= 0", name="ck_course_modules_position_nonnegative"),
    )
    op.create_index("ix_course_modules_course_id", "course_modules", ["course_id"])

    op.create_table(
        "lessons",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("module_id", sa.String(36), sa.ForeignKey("course_modules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("slug", sa.String(180), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_type", sa.String(16), server_default="ARTICLE", nullable=False),
        sa.Column("duration_minutes", sa.Integer(), server_default="5", nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("module_id", "slug", name="uq_lessons_module_slug"),
        sa.UniqueConstraint("module_id", "position", name="uq_lessons_module_position"),
        sa.CheckConstraint("content_type IN ('ARTICLE', 'VIDEO', 'RESOURCE')", name="ck_lessons_content_type"),
        sa.CheckConstraint("duration_minutes >= 0", name="ck_lessons_duration_nonnegative"),
        sa.CheckConstraint("position >= 0", name="ck_lessons_position_nonnegative"),
    )
    op.create_index("ix_lessons_module_id", "lessons", ["module_id"])

    op.create_table(
        "enrollments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", sa.String(36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(16), server_default="ACTIVE", nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("user_id", "course_id", name="uq_enrollments_user_course"),
        sa.CheckConstraint("status IN ('ACTIVE', 'COMPLETED', 'CANCELLED')", name="ck_enrollments_status"),
    )
    op.create_index("ix_enrollments_user_enrolled", "enrollments", ["user_id", "enrolled_at"])

    op.create_table(
        "lesson_progress",
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("lesson_id", sa.String(36), sa.ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_lesson_progress_lesson_id", "lesson_progress", ["lesson_id"])


def downgrade() -> None:
    op.drop_table("lesson_progress")
    op.drop_index("ix_enrollments_user_enrolled", table_name="enrollments")
    op.drop_table("enrollments")
    op.drop_index("ix_lessons_module_id", table_name="lessons")
    op.drop_table("lessons")
    op.drop_index("ix_course_modules_course_id", table_name="course_modules")
    op.drop_table("course_modules")
    for name in ("ix_courses_level", "ix_courses_category", "ix_courses_category_level", "ix_courses_catalog", "ix_courses_slug"):
        op.drop_index(name, table_name="courses")
    op.drop_table("courses")
    tables = set(inspect(op.get_bind()).get_table_names())
    if "ivoirex_legacy_enrollments" in tables:
        op.rename_table("ivoirex_legacy_enrollments", "enrollments")
    if "ivoirex_legacy_courses" in tables:
        op.rename_table("ivoirex_legacy_courses", "courses")
