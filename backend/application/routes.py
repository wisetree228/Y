"""
Модуль routes.py содержит маршруты FastAPI для обработки HTTP-запросов и WebSocket-соединений.
"""
from typing import Generator, Annotated
from fastapi import Response, WebSocket, APIRouter, Depends, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from backend.db.models import engine
from .utils import get_current_user_id, WebSocketConnectionManager
from .config import security, config
from .views import (
    register_view, login_view, create_post_view, create_comment_view,
    create_friendship_request_view, edit_profile_view, create_or_delete_like_view,
    vote_view, handle_websocket, add_media_to_post_view, get_posts_view,
    get_post_img_view, get_post_view, add_media_to_message_view,
    get_message_img_view, edit_post_view, delete_post_view, delete_comment_view,
    delete_vote_view, delete_message_view, change_avatar_view, get_avatar_view,
    get_chat_view, get_users_posts_view, get_my_page_view,
    get_other_page_view, get_is_friend_view, get_friends_view, delete_friend_view,
    get_friendship_requests_view, delete_friendship_request_view,
    delete_post_image_view, get_voted_users_view
)

from .schemas import (
    RegisterFormData, LoginFormData, CreatePostData, CreateCommentData, EditProfileFormData,
    EditPostData
)

router = APIRouter()
manager = WebSocketConnectionManager()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> Generator[AsyncSession, None, None]:
    """
    Генератор для получения сессии базы данных.

    Yields:
        AsyncSession: Асинхронная сессия базы данных.
    """
    async with SessionLocal() as db:
        yield db

SessionDep = Annotated[AsyncSession, Depends(get_db)]


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
    data: RegisterFormData, db: SessionDep
) -> dict:
    """
    Регистрирует нового пользователя.

    Args:
        data (RegisterFormData): Данные для регистрации.
        response (Response): Объект ответа FastAPI.
        db (AsyncSession): Сессия базы данных.

    Returns:
        dict: Результат регистрации.
    """
    return await register_view(data=data, db=db)


@router.post('/login')
async def login(
    data: LoginFormData, response: Response, db: SessionDep
) -> dict:
    """
    Аутентифицирует пользователя.

    Args:
        data (LoginFormData): Данные для входа.
        response (Response): Объект ответа FastAPI.
        db (AsyncSession): Сессия базы данных.

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
    data: CreatePostData, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Создает новый пост.

    Args:
        data (CreatePostData): Данные для создания поста.
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    return await create_post_view(data=data, user_id=int(user_id), db=db)


@router.post('/friendship_request/{getter_id}',
dependencies=[Depends(security.access_token_required)])
async def create_friendship_request(
    getter_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Создает запрос на дружбу.

    Args:
        getter_id (int): ID пользователя, получающего запрос.
        user_id (str): ID пользователя, отправляющего запрос.
        db (AsyncSession): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    return await create_friendship_request_view(author_id=int(user_id), getter_id=getter_id, db=db)


@router.put('/profile', dependencies=[Depends(security.access_token_required)])
async def edit_profile(
    data: EditProfileFormData, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Редактирует профиль пользователя.

    Args:
        data (EditProfileFormData): Данные для редактирования.
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    return await edit_profile_view(data=data, author_id=int(user_id), db=db)


@router.post('/post/{post_id}/comment', dependencies=[Depends(security.access_token_required)])
async def create_comment(
    post_id: int, data: CreateCommentData, db: SessionDep,
    user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Создает комментарий к посту.

    Args:
        data (CreateCommentData): Данные для создания комментария.
        post_id (int): ID поста.
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    return await create_comment_view(data=data, post_id=post_id, user_id=int(user_id), db=db)


@router.post('/post/{post_id}/like',
dependencies=[Depends(security.access_token_required)])
async def create_or_delete_like(
    post_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Создает или удаляет лайк на посте.

    Args:
        post_id (int): ID поста.
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    return await create_or_delete_like_view(post_id=post_id, user_id=int(user_id), db=db)


@router.post('/vote/{variant_id}', dependencies=[Depends(security.access_token_required)])
async def create_or_delete_vote(
    variant_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Создает или удаляет голос на варианте голосования.

    Args:
        variant_id (int): ID варианта голосования.
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.

    Returns:
        json: Статус операции.
    """
    return await vote_view(variant_id=variant_id, user_id=int(user_id), db=db)


@router.websocket("/chatsocket/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, db: SessionDep, user_id: str
) -> None:
    """
    Обрабатывает WebSocket-соединение для чата.

    Args:
        websocket (WebSocket): WebSocket-соединение.
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.
    """
    await handle_websocket(websocket=websocket, user_id=user_id, manager=manager, db=db)


@router.post('/posts/{post_id}/media', dependencies=[Depends(security.access_token_required)])
async def add_media_to_post(
    post_id: int, uploaded_file: UploadFile, db: SessionDep,
    user_id: str = Depends(get_current_user_id)
):
    """
    Добавляет в бд картинку, связанную с постом

    Args:
        uploaded_file (UploadFile): картинка от пользователя
        post_id (int): id поста
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.
    Returns:
        json: Статус операции
    """
    return await add_media_to_post_view(uploaded_file=uploaded_file,
    post_id=post_id, user_id=int(user_id), db=db)


@router.post('/message/{message_id}/media',
dependencies=[Depends(security.access_token_required)])
async def add_media_to_message(
    message_id: int, uploaded_file: UploadFile, db: SessionDep,
    user_id: str = Depends(get_current_user_id)
):
    """
    Добавляет в бд картинку, связанную с сообщением

    Args:
        uploaded_file (UploadFile): картинка от пользователя
        message_id (int): id сообщения
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.
    Returns:
        json: Статус операции
    """
    return await add_media_to_message_view(uploaded_file=uploaded_file,
    message_id=message_id, user_id=int(user_id), db=db)


@router.get('/posts', dependencies=[Depends(security.access_token_required)])
async def get_posts(
    db: SessionDep, user_id: str = Depends(get_current_user_id),
    skip: int = Query(0), limit: int = Query(100)
) -> dict:
    """
    Отдаёт данные для отрисовки ленты постов.

    Args:
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.
    Returns:
        json: Данные в виде json
    """
    return await get_posts_view(user_id=int(user_id), db=db, skip=skip, limit=limit)


@router.get('/posts/image/{image_id}', dependencies=[Depends(security.access_token_required)])
async def get_post_img(
    image_id: int, db: SessionDep
):
    """
    Отдаёт файл картинки, прикреплённой к посту

    Args:
        image_id (int): id картинки в бд
        db (AsyncSession): Сессия базы данных.
    Returns:
        StreamingResponse: файл картинки
    """
    return await get_post_img_view(image_id=image_id, db=db)


@router.get('/posts/{post_id}', dependencies=[Depends(security.access_token_required)])
async def get_post(
    post_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Отдаёт данные для просмотра одного поста.

    Args:
        post_id (int): ID поста
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.
    Returns:
        json: Данные в виде json
    """
    return await get_post_view(post_id=post_id, user_id=int(user_id), db=db)


@router.get('/message/image/{image_id}',
dependencies=[Depends(security.access_token_required)])
async def get_message_img(
    image_id: int, db: SessionDep
):
    """
    Отдаёт файл картинки, прикреплённой к сообщению

    Args:
        image_id (int): id картинки в бд
        db (AsyncSession): Сессия базы данных.
    Returns:
        StreamingResponse: файл картинки
    """
    return await get_message_img_view(image_id=image_id, db=db)


@router.put('/post/{post_id}', dependencies=[Depends(security.access_token_required)])
async def edit_post(
    post_id: int, data: EditPostData, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Редактирует пост

    Args:
        post_id (int): id поста
        user_id (str): ID пользователя.
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    return await edit_post_view(data=data, post_id=post_id, user_id=int(user_id), db=db)


@router.delete('/post/{post_id}', dependencies=[Depends(security.access_token_required)])
async def delete_post(
    post_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Удаляет пост

    Args:
        post_id (int): id поста
        user_id (str): ID пользователя.
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    return await delete_post_view(post_id=post_id, user_id=int(user_id), db=db)


@router.delete('/comment/{comment_id}', dependencies=[Depends(security.access_token_required)])
async def delete_comment(
    comment_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Удаляет комментарий

    Args:
        comment_id (int): id комментария
        user_id (str): ID пользователя.
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    return await delete_comment_view(comment_id=comment_id, user_id=int(user_id), db=db)


@router.delete('/vote/{post_id}', dependencies=[Depends(security.access_token_required)])
async def delete_vote(
    post_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Удаляет голос пользователя на варианте голосования в посте

    Args:
        post_id (int): id поста
        user_id (str): ID пользователя.
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    return await delete_vote_view(post_id=post_id, user_id=int(user_id), db=db)


@router.delete('/message/{message_id}', dependencies=[Depends(security.access_token_required)])
async def delete_message(
    message_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Удаляет сообщение

    Args:
        message_id (int): id варианта голосования
        user_id (str): ID пользователя.
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    return await delete_message_view(message_id=message_id, user_id=int(user_id), db=db)


@router.post('/avatar', dependencies=[Depends(security.access_token_required)])
async def change_avatar(
    uploaded_file: UploadFile, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Меняет аватарку пользователя

    Args:
        uploaded_file (UploadFile): загруженное изображение
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    return await change_avatar_view(uploaded_file=uploaded_file, user_id=int(user_id), db=db)


@router.get('/user/{another_user_id}/avatar',
dependencies=[Depends(security.access_token_required)])
async def get_avatar(
    another_user_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Возвращает аватарку пользователя

    Args:
        another_user_id (int): id пользователя, аватарку которого мы получаем
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        StreamingResponse - файл аватарки
    """
    return await get_avatar_view(another_user_id=another_user_id, user_id=int(user_id), db=db)


@router.get('/mypage/avatar', dependencies=[Depends(security.access_token_required)])
async def get_avatar(
    db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Возвращает аватарку пользователя

    Args:
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        StreamingResponse - файл аватарки
    """
    return await get_avatar_view(another_user_id=int(user_id), user_id=int(user_id), db=db)


@router.get('/chat/{recipient_id}', dependencies=[Depends(security.access_token_required)])
async def get_chat(
    recipient_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Возвращает данные для страницы чата (массив сообщений)

    Args:
        recipient_id (int): id собеседника
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - массив сообщений
    """
    return await get_chat_view(recipient_id=recipient_id, user_id=int(user_id), db=db)


@router.get('/profile/posts', dependencies=[Depends(security.access_token_required)])
async def get_users_posts(
    db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Возвращает список постов пользователя

    Args:
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - список постов
    """
    return await get_users_posts_view(user_id=int(user_id), db=db)


@router.get('/users/{user_id}/posts', dependencies=[Depends(security.access_token_required)])
async def get_user_posts(
    user_id: int, db: SessionDep
) -> dict:
    """
    Возвращает список постов пользователя

    Args:
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - список постов
    """
    return await get_users_posts_view(user_id=user_id, db=db)


@router.get('/mypage', dependencies=[Depends(security.access_token_required)])
async def get_my_page(
    db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Возвращает пользователю информацию о нём

    Args:
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - данные
    """
    return await get_my_page_view(user_id=int(user_id), db=db)


@router.get('/users/{other_user_id}', dependencies=[Depends(security.access_token_required)])
async def get_other_page(
    other_user_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Возвращает пользователю информацию о пользователе по id

    Args:
        other_user_id (int): id пользователя, информацию о котором мы получаем
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - данные
    """
    return await get_other_page_view(other_user_id=other_user_id, user_id=int(user_id), db=db)


@router.get('/isfriend/{friend_id}', dependencies=[Depends(security.access_token_required)])
async def get_is_friend(
    friend_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Возвращает пользователю, является ли этот человек другом или нет

    Args:
        friend_id_id (int): id пользователя, информацию о котором мы получаем
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - данные
    """
    return await get_is_friend_view(friend_id=friend_id, user_id=int(user_id), db=db)


@router.get('/friends', dependencies=[Depends(security.access_token_required)])
async def get_friends(
    db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Возвращает массив id пользователя

    Args:
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - данные
    """
    return await get_friends_view(user_id=int(user_id), db=db)


@router.delete('/friend/{friend_id}', dependencies=[Depends(security.access_token_required)])
async def delete_friend(
    friend_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Удаляет друга

    Args:
        friend_id (int): id друга
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    return await delete_friend_view(friend_id=friend_id, user_id=int(user_id), db=db)


@router.get('/friendship_requests', dependencies=[Depends(security.access_token_required)])
async def get_friendship_requests(
    db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Возвращает запросы дружбы, отправленные пользователю

    Args:
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - запросы дружбы
    """
    return await get_friendship_requests_view(user_id=int(user_id), db=db)


@router.delete('/friendship_request/{request_id}', dependencies=[Depends(security.access_token_required)])
async def delete_friendship_request(
    request_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Отклоняет входящий запрос дружбы

    Args:
        request_id (int): id запроса
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    return await delete_friendship_request_view(request_id=request_id, user_id=int(user_id), db=db)


@router.delete('/posts/image/{image_id}', dependencies=[Depends(security.access_token_required)])
async def delete_post_image(
    image_id: int, db: SessionDep, user_id: str = Depends(get_current_user_id)
) -> dict:
    """
    Удаляет изображение прикреплённое к посту

    Args:
        image_id (int): id картинки
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    return await delete_post_image_view(image_id=image_id, user_id=int(user_id), db=db)


@router.get('/voted_users/{voting_variant_id}', dependencies=[Depends(security.access_token_required)])
async def get_voted_users(voting_variant_id: int, db: SessionDep, user_id = Depends(get_current_user_id)) -> dict:
    """
    Возвращает информацию о проголосовавших за конкретный
    вариант голосования пользователей

    Args:
        voting_variant_id (int): id варианта голосования
        db (AsyncSession): сессия бд
        user_id (str): id пользователя
    Returns:
        json - данные
    """
    return await get_voted_users_view(voting_variant_id=voting_variant_id, user_id=int(user_id), db=db)