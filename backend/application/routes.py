"""
Модуль routes.py содержит маршруты FastAPI для обработки HTTP-запросов и WebSocket-соединений.
"""
from typing import Generator
from fastapi import Response, WebSocket, APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session
from backend.db.models import SessionLocal, AsyncSession
from .utils import get_current_user_id, WebSocketConnectionManager
from .config import security, config
from .views import *
from .schemas import (
    RegisterFormData, LoginFormData, CreatePostData, CreateCommentData, EditProfileFormData,
    EditPostData
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
        json: Статус операции.
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
    """
    Добавляет в бд картинку, связанную с постом
    Args:
        uploaded_file (UploadFile): картинка от пользователя
        post_id (int): id поста
        user_id (str): ID пользователя.
        db (Session): Сессия базы данных.
    Returns:
        json: Статус операции
    """
    return await add_media_to_post_view(uploaded_file=uploaded_file, post_id=post_id, user_id=int(user_id), db=db)

@router.post('/media_in_message/{message_id}', dependencies = [Depends(security.access_token_required)])
async def add_media_to_message(uploaded_file: UploadFile, message_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Добавляет в бд картинку, связанную с сообщением
    Args:
        uploaded_file (UploadFile): картинка от пользователя
        message_id (int): id сообщения
        user_id (str): ID пользователя.
        db (Session): Сессия базы данных.
    Returns:
        json: Статус операции
    """
    return await add_media_to_message_view(uploaded_file=uploaded_file, message_id=message_id, user_id=int(user_id), db=db)


@router.get('/posts', dependencies=[Depends(security.access_token_required)])
async def get_posts(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Отдаёт данные для отрисовки ленты постов.

    Args:
        user_id (str): ID пользователя.
        db (Session): Сессия базы данных.
    Returns:
        json: Данные в виде json
    """
    return await get_posts_view(user_id=int(user_id), db=db)


@router.get('/post_image/{image_id}', dependencies=[Depends(security.access_token_required)])
async def get_post_img(image_id: int, db: Session = Depends(get_db)):
    """
    Отдаёт файл картинки, прикреплённой к посту
    Args:
        image_id (int): id картинки в бд
        db (Session): Сессия базы данных.
    Returns:
        StreamingResponse: файл картинки
    """
    return await get_post_img_view(image_id = image_id, db=db)


@router.get('/post/{post_id}', dependencies=[Depends(security.access_token_required)])
async def get_post(post_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Отдаёт данные для просмотра одного поста.

    Args:
        post_id (int): ID поста
        user_id (str): ID пользователя.
        db (Session): Сессия базы данных.
    Returns:
        json: Данные в виде json
    """
    return await get_post_view(post_id=post_id, user_id=int(user_id), db=db)


@router.get('/message_image/{image_id}', dependencies=[Depends(security.access_token_required)])
async def get_message_img(image_id: int, db: Session = Depends(get_db)):
    """
    Отдаёт файл картинки, прикреплённой к сообщению
    Args:
        image_id (int): id картинки в бд
        db (Session): Сессия базы данных.
    Returns:
        StreamingResponse: файл картинки
    """
    return await get_message_img_view(image_id = image_id, db=db)


@router.put('/post/{post_id}', dependencies=[Depends(security.access_token_required)])
async def edit_post(data: EditPostData, post_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Редактирует пост
    Args:
        post_id (int): id поста
        user_id (str): ID пользователя.
        db (Session): сессия бд
    Returns:
        json - статус операции
    """
    return await edit_post_view(data = data, post_id = post_id, user_id = int(user_id), db = db)


@router.delete('/post/{post_id}', dependencies=[Depends(security.access_token_required)])
async def delete_post(post_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Удаляет пост
    Args:
        post_id (int): id поста
        user_id (str): ID пользователя.
        db (Session): сессия бд
    Returns:
        json - статус операции
    """
    return await delete_post_view(post_id = post_id, user_id = int(user_id), db = db)


@router.delete('/comment/{comment_id}', dependencies=[Depends(security.access_token_required)])
async def delete_comment(comment_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Удаляет комментарий
    Args:
        comment_id (int): id комментария
        user_id (str): ID пользователя.
        db (Session): сессия бд
    Returns:
        json - статус операции
    """
    return await delete_comment_view(comment_id = comment_id, user_id = int(user_id), db = db)


@router.delete('/vote/{variant_id}', dependencies=[Depends(security.access_token_required)])
async def delete_vote(variant_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Удаляет голос пользователя на варианте голосования
    Args:
        variant_id (int): id варианта голосования
        user_id (str): ID пользователя.
        db (Session): сессия бд
    Returns:
        json - статус операции
    """
    return await delete_vote_view(variant_id = variant_id, user_id = int(user_id), db = db)


@router.delete('/message/{message_id}', dependencies=[Depends(security.access_token_required)])
async def delete_message(message_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Удаляет сообщение
    Args:
        message_id (int): id варианта голосования
        user_id (str): ID пользователя.
        db (Session): сессия бд
    Returns:
        json - статус операции
    """
    return await delete_message_view(message_id = message_id, user_id = int(user_id), db = db)


@router.post('/avatar', dependencies=[Depends(security.access_token_required)])
async def change_avatar(uploaded_file: UploadFile, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Меняет аватарку пользователя
    Args:
        uploaded_file (UploadFile): загруженное изображение
        user_id (str): id пользователя
        db (Session): сессия бд
    Returns:
        json - статус операции
    """
    return await change_avatar_view(uploaded_file = uploaded_file, user_id = int(user_id), db = db)


@router.get('/avatar/{another_user_id}', dependencies=[Depends(security.access_token_required)])
async def get_avatar(another_user_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Возвращает аватарку пользователя
    Args:
        another_user_id (int): id пользователя, аватарку которого мы получаем
        user_id (str): id пользователя
        db (Session): сессия бд
    Returns:
        StreamingResponse - файл аватарки
    """
    return await get_avatar_view(another_user_id = another_user_id, user_id = int(user_id), db=db)


@router.get('/chat/{recipient_id}', dependencies=[Depends(security.access_token_required)])
async def get_chat(recipient_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Возвращает данные для страницы чата (массив сообщений)
    Args:
        recipient_id (int): id собеседника
        user_id (str): id пользователя
        db (Session): сессия бд
    Returns:
        json - массив сообщений
    """
    return await get_chat_view(recipient_id = recipient_id, user_id = int(user_id), db = db)


@router.get('/votes/{voting_variant_id}', dependencies=[Depends(security.access_token_required)])
async def get_votes(voting_variant_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Возвращает список голосовавших за вариант голосования в посте
    Args:
        voting_variant_id (int): id варианта голосования
        user_id (str): id пользователя
        db (Session): сессия бд
    Returns:
        json - список голосовавших
    """
    return await get_votes_view(voting_variant_id = voting_variant_id, user_id = int(user_id), db=db)


@router.get('/profile/posts', dependencies=[Depends(security.access_token_required)])
async def get_user_posts(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    Возвращает список постов пользователя
    Args:
        user_id (str): id пользователя
        db (Session): сессия бд
    Returns:
        json - список постов
    """
    return await get_users_posts_view(user_id = int(user_id), db=db)