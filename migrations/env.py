from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(base_dir)
from backend.db.models import Base

load_dotenv()

config = context.config

target_metadata = Base.metadata

def get_sync_url():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL не задана в файле .env или переменных окружения")
    return url.replace('postgresql+asyncpg', 'postgresql')

def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": get_sync_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()