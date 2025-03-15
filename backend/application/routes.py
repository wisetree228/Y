"""
Модуль routes.py содержит маршруты FastAPI для обработки HTTP-запросов и WebSocket-соединений.
"""
from typing import Generator
from fastapi import Response, WebSocket, APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session
from backend.db.models import SessionLocal, AsyncSession
from .utils import get_current_user_id, WebSocketConnectionManager
from .config import security, config
from .views import (
    register_view, login_view, create_post_view, create_comment_view,
    create_friendship_request_view, edit_profile_view, create_or_delete_like_view,
    vote_view, handle_websocket, add_media_to_post_view
)
from .schemas import (
    RegisterFormData, LoginFormData, CreatePostData, CreateCommentData, EditProfileFormData
)

router = APIRouter()
manager = WebSocketConnectionManager()


async def get_db() -> Generator[AsyncSession, None, None]:
    """
    Генератор для получения сессии базы данных.

    Yields:
        AsyncSession: Асинхронная сессия базы данных.
    """
    async with SessionLocal() as db:
        yield db


@router.get('/')
async def example() -> dict:
    """
    Пример эндпоинта для проверки работы API.

    Returns:
        dict: Статус операции.
    """
    return {'status': 'ok'}


@router.post('/register')
async def submit_form(
    data: RegisterFormData, response: Response, db: Session = Depends(get_db)
) -> dict:
    """
    Регистрирует нового пользователя.

    Args:
        data (RegisterFormData): Данные для регистрации.
        response (Response): Объект ответа FastAPI.
        db (Session): Сессия базы данных.

    Returns:
        dict: Результат регистрации.
    """
    return await register_view(data=data, response=response, db=db)


@router.post('/login')
async def login(
    data: LoginFormData, response: Response, db: Session = Depends(get_db)
) -> dict:
    """
    Аутентифицирует пользователя.

    Args:
        data (LoginFormData): Данные для входа.
        response (Response): Объект ответа FastAPI.
        db (Session): Сессия базы данных.

    Returns:
        dict: Токен аутентификации.
    """
    return await login_view(data=data, response=response, db=db)


@router.get('/my_id', dependencies=[Depends(security.access_token_required)])
async def secret(user_id: str = Depends(get_current_user_id)) -> dict:
    """
    Возвращает ID текущего пользователя.

    Args:
        user_id (str): ID пользователя.

    Returns:
        dict: ID пользователя.
    """
    return {'id': int(user_id)}


@router.post('/logout')
async def logout(response: Response) -> dict:
    """
    Выход пользователя из системы.

    Args:
        response (Response): Объект ответа FastAPI.

    Returns:
        dict: Статус операции.
    """
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    return {"status": "ok"}


@router.post('/post', dependencies=[Depends(security.access_token_required)])
async def create_post(
    data: CreatePostData, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)
) -> dict:
    """
    Создает новый пост.

    Args:
        data (CreatePostData): Данные для создания поста.
        user_id (str): ID пользователя.
        db (Session): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    return await create_post_view(data=data, user_id=int(user_id), db=db)


@router.post('/friendship_request/{getter_id}', dependencies=[Depends(security.access_token_required)])
async def create_friendship_request(
    getter_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)
) -> dict:
    """
    Создает запрос на дружбу.

    Args:
        getter_id (int): ID пользователя, получающего запрос.
        user_id (str): ID пользователя, отправляющего запрос.
        db (Session): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    return await create_friendship_request_view(author_id=int(user_id), getter_id=getter_id, db=db)


@router.put('/profile', dependencies=[Depends(security.access_token_required)])
async def edit_profile(
    data: EditProfileFormData, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)
) -> dict:
    """
    Редактирует профиль пользователя.

    Args:
        data (EditProfileFormData): Данные для редактирования.
        user_id (str): ID пользователя.
        db (Session): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    return await edit_profile_view(data=data, author_id=int(user_id), db=db)


@router.post('/comment/{post_id}', dependencies=[Depends(security.access_token_required)])
async def create_comment(
    data: CreateCommentData, post_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)
) -> dict:
    """
    Создает комментарий к посту.

    Args:
        data (CreateCommentData): Данные для создания комментария.
        post_id (int): ID поста.
        user_id (str): ID пользователя.
        db (Session): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    return await create_comment_view(data=data, post_id=post_id, user_id=int(user_id), db=db)


@router.post('/like/{post_id}', dependencies=[Depends(security.access_token_required)])
async def create_or_delete_like(
    post_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)
) -> dict:
    """
    Создает или удаляет лайк на посте.

    Args:
        post_id (int): ID поста.
        user_id (str): ID пользователя.
        db (Session): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    return await create_or_delete_like_view(post_id=post_id, user_id=int(user_id), db=db)


@router.post('/vote/{variant_id}', dependencies=[Depends(security.access_token_required)])
async def create_or_delete_vote(
    variant_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)
) -> dict:
    """
    Создает или удаляет голос на варианте голосования.

    Args:
        variant_id (int): ID варианта голосования.
        user_id (str): ID пользователя.
        db (Session): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    return await vote_view(variant_id=variant_id, user_id=int(user_id), db=db)


@router.websocket("/chat/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, user_id: str, db: Session = Depends(get_db)
) -> None:
    """
    Обрабатывает WebSocket-соединение для чата.

    Args:
        websocket (WebSocket): WebSocket-соединение.
        user_id (str): ID пользователя.
        db (Session): Сессия базы данных.
    """
    await handle_websocket(websocket=websocket, user_id=user_id, manager=manager, db=db)


@router.post('/media_in_post/{post_id}', dependencies = [Depends(security.access_token_required)])
async def add_media_to_post(uploaded_file: UploadFile, post_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return await add_media_to_post_view(uploaded_file=uploaded_file, post_id=post_id, user_id=int(user_id), db=db)