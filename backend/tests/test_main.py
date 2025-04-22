import os
import sys

# Это чтобы импорты нормально работали
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, '..', 'backend')
sys.path.append(backend_dir)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.db.models import Base  # Импортируем Base из моделей приложения

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
async_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    async_session_factory = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_factory() as session:
        yield session


@pytest.fixture
def override_get_db(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture
def client(override_get_db):
    return TestClient(app)


@pytest.mark.asyncio
async def test_base_url(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data == {'status': 'ok'}