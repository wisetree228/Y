import os
import sys

# Добавляем корень проекта в путь
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.db.models import Base  # Импортируем Base из моделей приложения


# Важно: Используйте переменную окружения для тестирования.
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")
async_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)


@pytest.fixture(scope="module")
async def db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield SessionLocal()
    finally:
        # Закрываем сессию
        await SessionLocal().close()


@pytest.fixture(scope="module")
def client(db):
    def get_test_client():
        return TestClient(app)

    client = get_test_client()
    return client


def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@pytest.mark.asyncio
async def test_something_with_db(client):
    """Пример теста, взаимодействующего с базой данных."""
    # Ваш код для работы с базой данных и отправки запросов к API здесь.
    response = client.get('/')  # Замена на ваш эндпоинт
    assert response.status_code == 200