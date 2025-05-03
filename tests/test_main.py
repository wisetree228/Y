import os
import sys

# Добавляем корень проекта в путь
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.db.models import Base  # Импортируем Base из моделей приложения
from backend.db.utils import (get_user_by_username)
from backend.application.schemas import (RegisterFormData, LoginFormData)
from backend.application.views import (register_view, login_view)


# Важно: Используйте переменную окружения для тестирования.
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")
async_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)


@pytest_asyncio.fixture(scope="module")
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

@pytest.mark.asyncio
async def test_register_success():
    async with SessionLocal() as db:
        data = RegisterFormData(
            username="testuser",
            email="test@example.com",
            name="Test",
            surname="User",
            password="1234"
        )

        result = await register_view(data, db)
        assert result == {'status': 'ok'}

        user = await get_user_by_username("testuser", db)
        assert user is not None
        assert user.email == "test@example.com"
        assert user.name == "Test"

@pytest.mark.asyncio
async def test_login_success():
    async with SessionLocal() as db:
        data = LoginFormData(
            email="test@example.com",
            password="1234"
        )

        response = Response()
        result = await login_view(data, response, db)
        assert "auth_token" in result
        assert isinstance(result["auth_token"], str)
