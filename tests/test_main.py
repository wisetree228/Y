import os
import sys

# Добавляем корень проекта в путь
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import json
import pytest
import pytest_asyncio
from httpx import AsyncClient
from httpx import ASGITransport
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.db.models import Base  # Импортируем Base из моделей приложения
from backend.application.config import (security, config)
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
async def test_base_api(client, db):
    """Пример теста, взаимодействующего с api."""
    response = await client.get('/')
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
async def test_upload_post_image(client):
    """
    Тест прикрепления картинки к посту
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)

    test_file = ("post_image.jpg", b"fake image data", "image/jpeg")

    response = await client.post(
        f"/posts/{1}/media",
        files={"uploaded_file": test_file}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_post_image(client):
    """
    Тест получения картинки к посту
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    response = await client.get(
        f"/posts/image/{1}"
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_post_image(client):
    """
    Тест удаления картинки из поста
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    response = await client.delete(
        f"/posts/image/{1}"
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_single_post(client):
    """
    Тест получения отдельного поста
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    response = await client.get(
        f"/posts/{1}"
    )
    assert response.status_code == 200


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


@pytest.mark.asyncio
async def test_websocket_chat():
    """
    Тестирование WebSocket чата:
    1. Подключение двух клиентов
    2. Отправка сообщения от первого клиента второму
    3. Проверка получения сообщения вторым клиентом
    """
    client = TestClient(app)
    with client.websocket_connect("/chatsocket/1") as websocket1:
        with client.websocket_connect("/chatsocket/2") as websocket2:
            test_message = {
                "recipient_id": "2",
                "message": "Hello from user 1"
            }

            websocket1.send_text(json.dumps(test_message))
            data = websocket2.receive_text()
            received_message = json.loads(data)

            assert received_message["author_id"] == "1"
            assert received_message["text"] == "Hello from user 1"
            assert "created_at" in received_message
            assert "id" in received_message


@pytest.mark.asyncio
async def test_upload_avatar(client):
    """
    Тест смены аватарки
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)

    test_file = ("post_image.jpg", b"fake image data", "image/jpeg")

    response = await client.post(
        "/avatar",
        files={"uploaded_file": test_file}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_logout(client):
    """
    Тест выхода из аккаунта
    """
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    response = await client.post(
        f"/logout"
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_message(client):
    token = security.create_access_token(uid="1")
    client.cookies.set(config.JWT_ACCESS_COOKIE_NAME, token)
    """
    Тест успешного удаления сообщения
        - пользователь авторизован
    Ожидается:
        статус код: 200
        json: {'status': 'ok'}
    """
    response = await client.delete(
        f'/message/{1}'
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.asyncio
async def test_login_fail_email(client):
    """
    Тест входа с неверной почтой
    Ожидается:
        статус код: 400
        json: {'detail': 'Пользователя с таким email не существует! Зарегистрируйтесь, пожалуйста.'}
    """
    response = await client.post(
        '/login',
        json={
            "email": "test@example.com",
            "password": "123"
        }
    )
    assert response.status_code == 400
    assert response.json() == {
        'detail': 'Пользователя с таким email не существует! Зарегистрируйтесь, пожалуйста.'
    }


@pytest.mark.asyncio
async def test_login_fail_password(client):
    """
    Тест входа с неверным паролем
    Ожидается:
        статус код: 200
        json: {'detail': 'Неверный пароль!'}
    """
    response = await client.post(
        '/login',
        json={
            "email": "user@example.com",
            "password": "123456"
        }
    )
    assert response.status_code == 400
    assert response.json() == {'detail': 'Неверный пароль!'}


@pytest.mark.asyncio
async def test_register_fail(client):
    """
    Тест регистрации с данными уже существующего пользователя
    Ожидается:
        статус код: 400
        json: {'detail': 'Пользователь с таким email уже существует.'}
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
    assert response.status_code == 400
    assert response.json() == {'detail': 'Пользователь с таким email уже существует.'}