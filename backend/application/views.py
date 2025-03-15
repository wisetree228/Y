"""
Импортирую необходимые для разработки утилиты и т. д.
"""
import json
from fastapi import HTTPException, Response, WebSocket, WebSocketDisconnect, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from backend.db.models import (
    User, Post, Comment, Vote, VotingVariant, Message, Friendship, FriendshipRequest, Like,
    MediaInPost
)
from backend.db.utils import (
    delete_object, add_and_refresh_object, get_user_by_email, get_user_by_id,
    get_post_by_id, get_like_on_post_from_user, get_likes_count, get_user_vote,
    get_user_by_username, get_existing_friendship, get_existing_friendship_request,
    get_message_by_id
)
from backend.application.utils import (
    hash_password, verify_password, WebSocketConnectionManager
)
from .schemas import (
    RegisterFormData, LoginFormData, CreatePostData, CreateCommentData, EditProfileFormData
)
from .config import config, security


async def register_view(data: RegisterFormData, response: Response, db: Session) -> dict:
    """
    Регистрирует нового пользователя.

    Args:
        data (RegisterFormData): Данные для регистрации.
        response (Response): Объект ответа FastAPI.
        db (Session): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    db_user_by_username = await get_user_by_username(data.username, db)
    db_user_by_email = await get_user_by_email(data.email, db)

    if db_user_by_username:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким юзернеймом уже существует."
        )
    if db_user_by_email:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует."
        )

    new_user = User(
        username=data.username,
        email=data.email,
        name=data.name,
        surname=data.surname,
        password=hash_password(data.password)
    )
    await add_and_refresh_object(new_user, db)

    token = security.create_access_token(uid=str(new_user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {'status': 'ok'}


async def login_view(data: LoginFormData, response: Response, db: Session) -> dict:
    """
    Аутентифицирует пользователя.

    Args:
        data (LoginFormData): Данные для входа.
        response (Response): Объект ответа FastAPI.
        db (Session): Сессия базы данных.

    Returns:
        dict: Токен аутентификации.
    """
    user = await get_user_by_email(data.email, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Пользователя с таким email не существует! Зарегистрируйтесь, пожалуйста."
        )
    if not verify_password(user.password, data.password):
        raise HTTPException(status_code=401, detail="Неверный пароль!")

    token = security.create_access_token(uid=str(user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"auth_token": token}


async def create_post_view(data: CreatePostData, user_id: int, db: Session) -> dict:
    """
    Создает новый пост.

    Args:
        data (CreatePostData): Данные для создания поста.
        user_id (int): ID автора поста.
        db (Session): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    post = Post(text=data.text, author_id=user_id)
    await add_and_refresh_object(post, db)

    if data.options:
        for option in data.options:
            var = VotingVariant(post_id=post.id, text=option)
            await add_and_refresh_object(var, db)

    return {'status': 'ok'}


async def create_friendship_request_view(
        author_id: int, getter_id: int, db: Session) -> dict:
    """
    Создает запрос на дружбу.

    Args:
        author_id (int): ID пользователя, отправляющего запрос.
        getter_id (int): ID пользователя, получающего запрос.
        db (Session): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    person = await get_user_by_id(getter_id, db)
    if not person:
        raise HTTPException(status_code=400, detail="Такого пользователя не существует.")

    existing_request = await get_existing_friendship_request(author_id, getter_id, db)
    if existing_request:
        raise HTTPException(
            status_code=400,
            detail="Вы уже отправили этому пользователю запрос дружбы!"
        )

    mutual_request = await get_existing_friendship_request(getter_id, author_id, db)
    existing_friendship = await get_existing_friendship(author_id, getter_id, db)

    if existing_friendship:
        raise HTTPException(
            status_code=400,
            detail="Вы уже дружите с этим пользователем!"
        )

    if mutual_request:
        new_friendship = Friendship(first_friend_id=author_id, second_friend_id=getter_id)
        await delete_object(mutual_request, db)
        await add_and_refresh_object(new_friendship, db)
        return {'status': 'you got a new friend!'}

    new_request = FriendshipRequest(author_id=author_id, getter_id=getter_id)
    await add_and_refresh_object(new_request, db)
    return {'status': 'запрос отправлен, ожидайте ответа от пользователя'}


async def edit_profile_view(
        data: EditProfileFormData, author_id: int, db: Session) -> dict:
    """
    Редактирует профиль пользователя.

    Args:
        data (EditProfileFormData): Данные для редактирования.
        author_id (int): ID пользователя.
        db (Session): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    db_user_by_username = await get_user_by_username(data.username, db)
    db_user_by_email = await get_user_by_email(data.email, db)

    if db_user_by_username:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким юзернеймом уже существует."
        )
    if db_user_by_email:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует."
        )

    user = await get_user_by_id(author_id, db)
    if data.username:
        user.username = data.username
    if data.email:
        user.email = data.email
    if data.name:
        user.name = data.name
    if data.surname:
        user.surname = data.surname
    if data.password:
        user.password = hash_password(data.password)

    await db.commit()
    await db.refresh(user)
    return {'status': 'ok'}


async def create_comment_view(
        data: CreateCommentData, post_id: int, user_id: int, db: Session) -> dict:
    """
    Создает комментарий к посту.

    Args:
        data (CreateCommentData): Данные для создания комментария.
        post_id (int): ID поста.
        user_id (int): ID автора комментария.
        db (Session): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    post = await get_post_by_id(post_id, db)
    if not post:
        raise HTTPException(status_code=400, detail="Поста с таким id не существует!")

    comment = Comment(text=data.text, post_id=post_id, author_id=user_id)
    await add_and_refresh_object(comment, db)
    return {'status': 'ok'}


async def create_or_delete_like_view(post_id: int, user_id: int, db: Session) -> dict:
    """
    Создает или удаляет лайк на посте.

    Args:
        post_id (int): ID поста.
        user_id (int): ID пользователя.
        db (Session): Сессия базы данных.

    Returns:
        dict: Статус операции и количество лайков.
    """
    post = await get_post_by_id(post_id, db)
    if not post:
        raise HTTPException(status_code=400, detail="Такого поста не существует!")

    like = await get_like_on_post_from_user(post_id, user_id, db)
    if not like:
        new_like = Like(post_id=post_id, author_id=user_id)
        await add_and_refresh_object(new_like, db)
        return {'status': 'liked', 'likes_count': await get_likes_count(post_id, db)}

    await delete_object(like, db)
    return {'status': 'unliked', 'likes_count': await get_likes_count(post_id, db)}


async def handle_websocket(
        websocket: WebSocket, user_id: str, manager: WebSocketConnectionManager, db: Session) -> None:
    """
    Обрабатывает WebSocket-соединение.

    Args:
        websocket (WebSocket): WebSocket-соединение.
        user_id (str): ID пользователя.
        manager (WebSocketConnectionManager): Менеджер соединений.
        db (Session): Сессия базы данных.
    """
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            recipient_id = message_data.get("recipient_id")
            message = message_data.get("message")

            if recipient_id and message:
                await manager.send_personal_message(f"User {user_id}: {message}", recipient_id)
                new_message = Message(
                    text=message,
                    author_id=int(user_id),
                    getter_id=int(recipient_id)
                )
                await add_and_refresh_object(new_message, db)
            else:
                await websocket.send_text("Invalid message format")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.send_personal_message(f"User {user_id} left the chat", recipient_id)


async def vote_view(variant_id: int, user_id: int, db: Session) -> dict:
    """
    Обрабатывает голосование.

    Args:
        variant_id (int): ID варианта голосования.
        user_id (int): ID пользователя.
        db (Session): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    var = await db.execute(
        select(VotingVariant)
        .where(VotingVariant.id == variant_id)
        .options(selectinload(VotingVariant.post).selectinload(Post.voting_variants))
    )
    var = var.scalars().first()

    if not var:
        raise HTTPException(status_code=400, detail="Такого варианта голосования не существует!")

    for variant in var.post.voting_variants:
        vote = await get_user_vote(variant.id, user_id, db)
        if vote:
            await delete_object(vote, db)

    new_vote = Vote(user_id=user_id, variant_id=variant_id)
    await add_and_refresh_object(new_vote, db)
    return {'status': 'ok'}


async def add_media_to_post_view(uploaded_file: UploadFile, post_id: int, user_id: int, db: Session):
    post = get_post_by_id(id=post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    if post.author_id != user_id:
        raise HTTPException(status_code=403, detail="Вы не являетесь автором поста")
    
    file_bytes = await uploaded_file.read()

    new_media = MediaInPost(post_id=post_id, image=file_bytes)

    await add_and_refresh_object(object=new_media, db=db)
    return {'status': 'file successfully added'}


async def add_media_to_message_view(uploaded_file: UploadFile, message_id: int, user_id: int, db: Session):
    message = get_message_by_id(id=message_id)

    if not message:
        raise HTTPException(status_code=404, detail="Пост не найден")

    if message.author_id != user_id:
        raise HTTPException(status_code=403, detail="Вы не являетесь автором поста")

    file_bytes = await uploaded_file.read()

    new_media = MediaInPost(post_id=message_id, image=file_bytes)

    await add_and_refresh_object(object=new_media, db=db)
    return {'status': 'file successfully added'}
