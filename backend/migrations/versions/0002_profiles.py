"""Add editable member profiles and preserve legacy user profile fields."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, select

revision = "0002_profiles"
down_revision = "0001_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    if "profiles" not in inspect(op.get_bind()).get_table_names():
        op.create_table(
            "profiles",
            sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("display_name", sa.String(80), nullable=False),
            sa.Column("bio", sa.String(280), server_default="", nullable=False),
            sa.Column("city", sa.String(64), server_default="Abidjan", nullable=False),
            sa.Column("country", sa.String(64), server_default="Côte d’Ivoire", nullable=False),
            sa.Column("skills", sa.JSON(), server_default="[]", nullable=False),
            sa.Column("interests", sa.JSON(), server_default="[]", nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
    connection = op.get_bind()
    inspector = inspect(connection)
    columns = {column["name"] for column in inspector.get_columns("users")}
    legacy_select = ["id", "username"]
    for name in ("bio", "city", "skills"):
        legacy_select.append(name if name in columns else sa.literal("").label(name))
    rows = connection.execute(select(*[sa.column(name) if isinstance(name, str) else name for name in legacy_select]).select_from(sa.table("users"))).mappings()
    profile_table = sa.table(
        "profiles",
        sa.column("user_id", sa.String),
        sa.column("display_name", sa.String),
        sa.column("bio", sa.String),
        sa.column("city", sa.String),
        sa.column("country", sa.String),
        sa.column("skills", sa.JSON),
        sa.column("interests", sa.JSON),
    )
    for row in rows:
        skills = [item.strip() for item in (row["skills"] or "").split(",") if item.strip()]
        connection.execute(profile_table.insert().values(
            user_id=row["id"], display_name=row["username"], bio=(row["bio"] or "")[:280],
            city=row["city"] or "Abidjan", country="Côte d’Ivoire", skills=skills[:12], interests=[],
        ))


def downgrade() -> None:
    if "profiles" in inspect(op.get_bind()).get_table_names():
        op.drop_table("profiles")
