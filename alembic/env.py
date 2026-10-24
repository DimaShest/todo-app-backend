import sys
from pathlib import Path

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from app.models.task import TaskORM # noqa
from app.models.category import CategoryORM # noqa
from app.models.base import Base


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

print("DATABASE_URL:", get_settings().database_url)  # Добавьте эту строку для отладки
config.set_main_option("sqlalchemy.url", get_settings().database_url)
##metadata хранит схему и описание таблиц — имена таблиц, столбцы, ключи, ограничения и связи, присвоенную при определении классов моделей. Alembic использует эту метадату для сравнения с текущей схемой базы данных и генерации миграций. 
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            compare_server_default=True  # добавляем параметр compare_server_default, чтобы Alembic учитывал изменения в значениях по умолчанию при генерации миграций
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
