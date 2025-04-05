import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.db.models import *


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
async_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with SessionLocal() as db:
        yield db



@pytest.fixture(autouse=True) # autouse=True: Эта фикстура автоматически применяется ко всем тестам без явного вызова.
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
    app.dependency_overrides[get_db] = lambda: db_session

@pytest.fixture
def client(override_get_db):
    return TestClient(app)

@pytest.mark.asyncio
async def test_base_url(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()["status"]
    assert data == "ok"

# @pytest.mark.asyncio
# async def test_read_tasks(client):
#     client.post("/tasks/", json={"title": "Task 1"})
#     client.post("/tasks/", json={"title": "Task 2"})
#     response = client.get("/tasks/")
#     assert response.status_code == 200
#     data = response.json()["tasks"]
#     assert len(data) == 2
#     assert data[0]["title"] == "Task 1"
#     assert data[1]["title"] == "Task 2"
#
# @pytest.mark.asyncio
# async def test_update_task(client):
#     response = client.post("/tasks/", json={"title": "Task to Update"})
#     task_id = response.json()["task"]["id"]
#     response = client.put(f"/tasks/{task_id}/", json={"completed": True})
#     assert response.status_code == 200
#     data = response.json()["task"]
#     assert data["completed"] is True