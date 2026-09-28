from alembic import context
from sqlalchemy import engine_from_config, pool
from app.core.database import Base
from app.core.settings import settings
from app.models import domain  # noqa: F401
config = context.config
target_metadata = Base.metadata
def run_migrations_offline():
    context.configure(url=settings.database_url, target_metadata=target_metadata, literal_binds=True, compare_type=True)
    with context.begin_transaction(): context.run_migrations()
def run_migrations_online():
    section = config.get_section(config.config_ini_section) or {}
    section["sqlalchemy.url"] = settings.database_url
    connectable = engine_from_config(section, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction(): context.run_migrations()
if context.is_offline_mode(): run_migrations_offline()
else: run_migrations_online()
