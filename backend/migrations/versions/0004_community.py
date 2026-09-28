"""Add persisted community posts, comments and member reactions."""
from alembic import op
import sqlalchemy as sa

revision = "0004_community"
down_revision = "0003_campus"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "community_posts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("length(trim(title)) > 0", name="ck_community_posts_title_nonempty"),
        sa.CheckConstraint("length(trim(content)) > 0", name="ck_community_posts_content_nonempty"),
    )
    op.create_index("ix_community_posts_user_id", "community_posts", ["user_id"])
    op.create_index("ix_community_posts_created", "community_posts", ["created_at", "id"])
    op.create_table(
        "community_comments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("post_id", sa.String(36), sa.ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("length(trim(content)) > 0", name="ck_community_comments_content_nonempty"),
    )
    op.create_index("ix_community_comments_user_id", "community_comments", ["user_id"])
    op.create_index("ix_community_comments_post_created", "community_comments", ["post_id", "created_at"])
    op.create_table(
        "community_reactions",
        sa.Column("post_id", sa.String(36), sa.ForeignKey("community_posts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_community_reactions_user_id", "community_reactions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_community_reactions_user_id", table_name="community_reactions")
    op.drop_table("community_reactions")
    op.drop_index("ix_community_comments_post_created", table_name="community_comments")
    op.drop_index("ix_community_comments_user_id", table_name="community_comments")
    op.drop_table("community_comments")
    op.drop_index("ix_community_posts_created", table_name="community_posts")
    op.drop_index("ix_community_posts_user_id", table_name="community_posts")
    op.drop_table("community_posts")
