import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool, text
from sqlalchemy.ext.asyncio import async_engine_from_config

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from alembic import context
from config import settings

# Импортируем ВСЕ модели явно (критически важно!)
from core.models import (
    AccessRule,
    Base,
    BusinessElement,
    Project,
    RefreshToken,
    Role,
    User,
    UserRole,
)

# Alembic Config
config = context.config

# Устанавливаем URL из настроек
config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL") or settings.db.url)

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata для автогенерации
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Оффлайн режим"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Выполняет миграции"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Онлайн режим через async engine"""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url")

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
