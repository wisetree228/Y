import os
import sys

# Добавляем корень проекта в путь
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from httpx import ASGITransport
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.db.models import Base  # Импортируем Base из моделей приложения
from backend.application.config import (security, config)
from backend.db.utils import (get_likes_count)
from backend.application.routes import (get_db)

# Важно: Используйте переменную окружения для тестирования.
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")
async_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=async_engine, 
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture(scope="module")
async def db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield SessionLocal()
    finally:
        # Закрываем сессию
        await clear_data()
        await SessionLocal().close()


@pytest_asyncio.fixture(scope="module")
async def client():
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

async def clear_data():
    async with async_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())

async def override_get_db():
    async with SessionLocal() as session:
        yield session


@pytest.mark.asyncio
async def test_something_with_db(client, db):
    """Пример теста, взаимодействующего с базой данных."""
    # Ваш код для работы с базой данных и отправки запросов к API здесь.
    response = await client.get('/')  # Замена на ваш эндпоинт
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_register(client):
    """
    Тест регистрации пользователя при валидных данных
    Ожидается:
        статус код: 200
        json: {'status': 'ok'}
    """
    response = await client.post(
        '/register',
        json={
            "email": "user@example.com",
            "username": "test",
            "name": "user",
            "surname": "testuser",
            "password": "123"
        }
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_login(client):
    """
    Тест входа существующего пользователя 
    Ожидается:
        статус код: 200
    """
    response = await client.post(
        '/login',
        json={
            "email": "user@example.com",
            "password": "123"
        }
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_logout(client):
    """
    Тест выхода авторизированного пользователя
    Ожидается:
        статус код: 200
        json: {'status': 'ok'}
    """
    response = await client.post(
        '/logout'
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}

@pytest.mark.asyncio
async def test_create_post(client):
    token = security.create_access_token(uid="1") 
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    """
    Тест успешного создания поста 
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json: {'status': 'ok'}
    """ 
    response = await client.post(
        '/post',
        json={
            "text": "string",
            "options": [
                "string"
            ]
        }
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_create_comment(client):
    """
    Тест успешного создания комментария
        - пользователь авторизован
        - пост существует
    Ожидается:
        статус код: 200
        json: {'status': 'ok'}
    """
    token = security.create_access_token(uid="1") 
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token) 
    response = await client.post(
        f'/post/{1}/comment',
        json={
            "text": "string"
        }
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_create_like(client):
    """
    Тест добавления лайка к посту
        - пользователь авторизован
        - пост существует
    Ожидается:
        статус код: 200
        json: {'status': 'liked', 'likes_count': 1}
    """
    token = security.create_access_token(uid="1") 
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token) 
    response = await client.post(
        f'/post/{1}/like'
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'liked', 'likes_count': 1}

@pytest.mark.asyncio
async def test_delete_like(client):
    """
    Тест удаления лайка у поста
        - пользователь авторизован
        - пост существует
    Ожидается:
        статус код: 200
        json: {'status': 'unliked', 'likes_count': 0}
    """
    token = security.create_access_token(uid="1") 
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token) 
    response = await client.post(
        f'/post/{1}/like'
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'unliked', 'likes_count': 0}


@pytest.mark.asyncio
async def test_get_posts(client):
    """
    Тест получения списка постов
        - пользователь авторизован
    Ожидается:
        статус код: 200
    """
    token = security.create_access_token(uid="1") 
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token) 

    response = await client.get(
        '/posts'
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_register_2(client):
    """
    Тест регистрации второго пользователя (для проверки дружбы)
    Ожидается:
        статус код: 200
        json: {'status': 'ok'}
    """
    response = await client.post(
        '/register',
        json={
            "email": "user2@example.com",
            "username": "test2",
            "name": "user2",
            "surname": "testuser2",
            "password": "123"
        }
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_send_friendship_request(client):
    """
    Тест отправки запроса дружбы
        - пользователь авторизован
    Ожидается:
        статус код: 200
    """
    token = security.create_access_token(uid="2")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)

    response = await client.post(
        f'/friendship_request/{1}'
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_friendship_requests(client):
    """
    Тест получения входящих запросов дружбы
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json в нужном формате
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)

    response = await client.get(
        f'/friendship_requests'
    )
    assert response.status_code == 200
    assert response.json() == {
        "friendship_requests": [
        {
            "id": 1,
            "author_id": 2,
            "author_username": "test2"
        }
    ]
    }

@pytest.mark.asyncio
async def test_reject_friendship_request(client):
    """
    Тест отклонения входящего запроса дружбы
        - пользователь авторизован
    Ожидается:
        статус код: 200
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)

    response = await client.delete(
        f'/friendship_request/{1}'
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_someones_avatar(client):
    """
    Тест получения чьей-то аватарки
        - пользователь авторизован
    Ожидается:
        статус код: 200
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)

    response = await client.get(
        f'/user/{2}/avatar'
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_vote(client):
    """
    Тест голосования
        - пользователь авторизован
    Ожидается:
        статус код: 200
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)

    response = await client.post(
        f'/vote/{1}'
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_vote(client):
    """
    Тест отмены голосования на посте
        - пользователь авторизован
    Ожидается:
        статус код: 200
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)

    response = await client.delete(
        f'/vote/{1}'
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_edit_post(client):
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    """
    Тест успешного редактирования поста 
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json: {'status': 'ok'}
    """
    response = await client.put(
        f'/post/{1}',
        json={
            "text": "string2"
        }
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_complaint_comment(client):
    """
    Тест успешного создания жалобы на комментарий
        - пользователь авторизован
        - пост существует
    Ожидается:
        статус код: 200
        json: {'status': 'ok'}
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    response = await client.post(
        f'/complaint_comment/{1}'
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_delete_comment(client):
    """
    Тест успешного удаления комментария
        - пользователь авторизован
        - пост существует
    Ожидается:
        статус код: 200
        json: {'status': 'ok'}
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    response = await client.delete(
        f'/comment/{1}'
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_complaint_post(client):
    """
    Тест успешного создания жалобы на пост
        - пользователь авторизован
        - пост существует
    Ожидается:
        статус код: 200
        json: {'status': 'ok'}
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    response = await client.post(
        f'/complaint_post/{1}'
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_get_voted_users(client):
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    """
    Тест получения голосовавших пользователей
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json в нужном формате
    """
    response = await client.get(
        f'/voted_users/{1}'
    )
    assert response.status_code == 200
    assert response.json() == {
        'users': []
    }


@pytest.mark.asyncio
async def test_delete_post(client):
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    """
    Тест успешного удаления поста
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json: {'status': 'ok'}
    """
    response = await client.delete(
        f'/post/{1}'
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_get_chat(client):
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    """
    Тест получения чата с пользователем
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json в нужном формате
    """
    response = await client.get(
        f'/chat/{2}'
    )
    assert response.status_code == 200
    assert response.json() == {
        "recipient_id": 2,
        "recipient_username": "test2",
        "messages": []
    }


@pytest.mark.asyncio
async def test_get_user_posts(client):
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    """
    Тест получения постов пользователя
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json в нужном формате
    """
    response = await client.get(
        f'/users/{2}/posts'
    )
    assert response.status_code == 200
    assert response.json() == {'posts':[]}


@pytest.mark.asyncio
async def test_get_profile(client):
    token = security.create_access_token(uid="2")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    """
    Тест получения своего профиля
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json в нужном формате
    """
    response = await client.get(
        f'/mypage'
    )
    assert response.status_code == 200
    assert response.json() == {
        'username':'test2',
        'name':'user2',
        'surname':'testuser2',
        'email':'user2@example.com',
        'posts': []
    }


@pytest.mark.asyncio
async def test_get_other_profile(client):
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    """
    Тест получения чужого профиля
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json в нужном формате
    """
    response = await client.get(
        f'/users/{2}'
    )
    assert response.status_code == 200
    assert response.json() == {
        'username':'test2',
        'name':'user2',
        'surname':'testuser2',
        'email':'user2@example.com',
        'posts': []
    }


@pytest.mark.asyncio
async def test_get_friends(client):
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    """
    Тест получения списка друзей
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json в нужном формате
    """
    response = await client.get(
        f'/friends'
    )
    assert response.status_code == 200
    assert response.json() == {
        'friends_list':[]
    }


@pytest.mark.asyncio
async def test_edit_profile(client):
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    """
    Тест редактирования профиля
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json: {'status': 'ok'}
    """
    response = await client.put(
        f'/profile',
        json={
            'name':'new_name',
            'username':'new_username'
        }
    )
    assert response.status_code == 200
    assert response.json() == {'status':'ok'}


@pytest.mark.asyncio
async def test_get_user_posts(client):
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    """
    Тест получения своих постов
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json в нужном формате
    """
    response = await client.get(
        f'/profile/posts'
    )
    assert response.status_code == 200
    assert response.json() == {'posts':[]}


@pytest.mark.asyncio
async def test_get_is_friend(client):
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    """
    Тест получения информации о том дружит ли один пользователь с другим
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json в нужном формате
    """
    response = await client.get(
        f'/isfriend/{2}'
    )
    assert response.status_code == 200
    assert response.json() == {'isFriend':False}


@pytest.mark.asyncio
async def test_send_friendship_request2(client):
    """
    Повторный тест отправки запроса дружбы(на этот раз одобряем)
        - пользователь авторизован
    Ожидается:
        статус код: 200
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)

    response = await client.post(
        f'/friendship_request/{2}'
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_accept_friendship_request(client):
    """
    Тест одобрения входящей дружбы
        - пользователь авторизован
    Ожидается:
        статус код: 200
    """
    token = security.create_access_token(uid="2")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)

    response = await client.post(
        f'/friendship_request/{1}'
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_friend(client):
    """
    Тест удаления друга
        - пользователь авторизован
    Ожидается:
        статус код: 200
    """
    token = security.create_access_token(uid="2")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)

    response = await client.delete(
        f'/friend/{1}'
    )
    assert response.status_code == 200