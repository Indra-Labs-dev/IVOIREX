"""Create the identity table or adopt the legacy users table without data loss."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
revision = "0001_users"
down_revision = None
branch_labels = None
depends_on = None
def upgrade() -> None:
    inspector = inspect(op.get_bind())
    if "users" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("users")}
        required = {"id", "email", "username", "password_hash", "role", "created_at"}
        missing = required - columns
        if missing:
            raise RuntimeError(f"Existing users table is missing required columns: {sorted(missing)}")
        if "token_version" not in columns:
            op.add_column("users", sa.Column("token_version", sa.Integer(), server_default="0", nullable=False))
        indexes = {index["name"] for index in inspector.get_indexes("users")}
        if "ix_users_email" not in indexes:
            op.create_index("ix_users_email", "users", ["email"], unique=True)
        if "ix_users_username" not in indexes:
            op.create_index("ix_users_username", "users", ["username"], unique=True)
        return
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(32), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("bio", sa.Text(), server_default="", nullable=False),
        sa.Column("city", sa.String(64), server_default="Abidjan", nullable=False),
        sa.Column("skills", sa.Text(), server_default="", nullable=False),
        sa.Column("xp", sa.Integer(), server_default="0", nullable=False),
        sa.Column("streak", sa.Integer(), server_default="1", nullable=False),
        sa.Column("reputation", sa.Integer(), server_default="0", nullable=False),
        sa.Column("role", sa.String(16), server_default="USER", nullable=False),
        sa.Column("token_version", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)
def downgrade() -> None:
    inspector = inspect(op.get_bind())
    if "users" in inspector.get_table_names() and "token_version" in {column["name"] for column in inspector.get_columns("users")}:
        op.drop_column("users", "token_version")
