"""
Импортирую необходимые для разработки утилиты и т. д.
"""
import json
from io import BytesIO
from fastapi import (HTTPException, Response, WebSocket, WebSocketDisconnect,
    UploadFile
)
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from backend.db.models import (
    User, Post, Comment, Vote, VotingVariant, Message, Friendship, FriendshipRequest, Like,
    MediaInPost, MediaInMessage, ComplaintAboutPost, ComplaintAboutComment
)
from backend.db.utils import (
    delete_object, add_and_refresh_object, get_user_by_email,
    get_like_on_post_from_user, get_likes_count, get_user_vote,
    get_user_by_username, get_existing_friendship, get_existing_friendship_request,
    get_all_from_table, get_post_voting_variants, get_object_by_id,
    get_messages_between_two_users, get_images_id_for_message, get_votes_on_voting_variant,
    get_user_posts, get_user_friends, get_friendship_requests_for_user

)
from backend.application.utils import (
    hash_password, verify_password, WebSocketConnectionManager, process_voting_variants
)
from .schemas import (
    RegisterFormData, LoginFormData, CreatePostData, CreateCommentData, EditProfileFormData,
    EditPostData
)
from .config import config, security


async def register_view(data: RegisterFormData, response: Response, db: AsyncSession) -> dict:
    """
    Регистрирует нового пользователя.

    Args:
        data (RegisterFormData): Данные для регистрации.
        response (Response): Объект ответа FastAPI.
        db (AsyncSession): Сессия базы данных.

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


async def login_view(data: LoginFormData, response: Response, db: AsyncSession) -> dict:
    """
    Аутентифицирует пользователя.

    Args:
        data (LoginFormData): Данные для входа.
        response (Response): Объект ответа FastAPI.
        db (AsyncSession): Сессия базы данных.

    Returns:
        dict: Токен аутентификации.
    """
    user = await get_user_by_email(data.email, db)
    if not user:
        raise HTTPException(
            status_code=402,
            detail="Пользователя с таким email не существует! Зарегистрируйтесь, пожалуйста."
        )
    if not verify_password(user.password, data.password):
        raise HTTPException(status_code=401, detail="Неверный пароль!")

    token = security.create_access_token(uid=str(user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"auth_token": token}


async def create_post_view(data: CreatePostData, user_id: int, db: AsyncSession) -> dict:
    """
    Создает новый пост.

    Args:
        data (CreatePostData): Данные для создания поста.
        user_id (int): ID автора поста.
        db (AsyncSession): Сессия базы данных.

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
        author_id: int, getter_id: int, db: AsyncSession) -> dict:
    """
    Создает запрос на дружбу.

    Args:
        author_id (int): ID пользователя, отправляющего запрос.
        getter_id (int): ID пользователя, получающего запрос.
        db (AsyncSession): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    person = await get_object_by_id(object_type=User, id=getter_id, db=db)
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
        data: EditProfileFormData, author_id: int, db: AsyncSession) -> dict:
    """
    Редактирует профиль пользователя.

    Args:
        data (EditProfileFormData): Данные для редактирования.
        author_id (int): ID пользователя.
        db (AsyncSession): Сессия базы данных.

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

    user = await get_object_by_id(object_type=User, id=author_id, db=db)
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
        data: CreateCommentData, post_id: int, user_id: int, db: AsyncSession) -> dict:
    """
    Создает комментарий к посту.

    Args:
        data (CreateCommentData): Данные для создания комментария.
        post_id (int): ID поста.
        user_id (int): ID автора комментария.
        db (AsyncSession): Сессия базы данных.

    Returns:
        dict: Статус операции.
    """
    post = await get_object_by_id(object_type=Post, id=post_id, db=db)
    if not post:
        raise HTTPException(status_code=400, detail="Поста с таким id не существует!")

    comment = Comment(text=data.text, post_id=post_id, author_id=user_id)
    await add_and_refresh_object(comment, db)
    return {'status': 'ok'}


async def create_or_delete_like_view(post_id: int, user_id: int, db: AsyncSession) -> dict:
    """
    Создает или удаляет лайк на посте.

    Args:
        post_id (int): ID поста.
        user_id (int): ID пользователя.
        db (AsyncSession): Сессия базы данных.

    Returns:
        dict: Статус операции и количество лайков.
    """
    post = await get_object_by_id(object_type=Post, id=post_id, db=db)
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
        websocket: WebSocket, user_id: str, manager: WebSocketConnectionManager, db: AsyncSession) -> None:
    """
    Обрабатывает WebSocket-соединение.

    Args:
        websocket (WebSocket): WebSocket-соединение.
        user_id (str): ID пользователя.
        manager (WebSocketConnectionManager): Менеджер соединений.
        db (AsyncSession): Сессия базы данных.
    """
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            recipient_id = message_data.get("recipient_id")
            message = message_data.get("message")

            if recipient_id and message:
                new_message = Message(
                    text=message,
                    author_id=int(user_id),
                    getter_id=int(recipient_id)
                )
                await add_and_refresh_object(new_message, db)
                await manager.send_personal_message(message_id=new_message.id, author_id=user_id, text=message, user_id=recipient_id)
            else:
                await websocket.send_text("Invalid message format")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        #await manager.send_personal_message(f"User {user_id} left the chat", recipient_id)


async def vote_view(variant_id: int, user_id: int, db: AsyncSession) -> dict:
    """
    Обрабатывает голосование.

    Args:
        variant_id (int): ID варианта голосования.
        user_id (int): ID пользователя.
        db (AsyncSession): Сессия базы данных.

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


async def add_media_to_post_view(uploaded_file: UploadFile, post_id: int, user_id: int, db: AsyncSession):
    """
    Добавляет в бд картинку, связанную с постом
    Args:
        uploaded_file (UploadFile): картинка от пользователя
        post_id (int): id поста
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.
    Returns:
        dict: Статус операции
    """
    post = await get_object_by_id(object_type=Post, id=post_id, db=db)
    
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    if post.author_id != user_id:
        raise HTTPException(status_code=403, detail="Вы не являетесь автором поста")
    
    file_bytes = await uploaded_file.read()

    new_media = MediaInPost(post_id=post_id, image=file_bytes)

    await add_and_refresh_object(object=new_media, db=db)
    return {'status': 'file successfully added'}


async def add_media_to_message_view(uploaded_file: UploadFile, message_id: int, user_id: int, db: AsyncSession):
    """
    Добавляет в бд картинку, связанную с сообщением
    Args:
        uploaded_file (UploadFile): картинка от пользователя
        message_id (int): id сообщения
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.
    Returns:
        dict: Статус операции
    """
    message = await get_object_by_id(object_type=Message, id=message_id, db=db)
    
    if not message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")

    if message.author_id != user_id:
        raise HTTPException(status_code=403, detail="Вы не являетесь автором сообщения")
    
    file_bytes = await uploaded_file.read()

    new_media = MediaInMessage(message_id=message_id, image=file_bytes)

    await add_and_refresh_object(object=new_media, db=db)
    return {'status': 'file successfully added'}


async def get_posts_view(user_id: int, db: AsyncSession):
    """
    Отдаёт данные для отрисовки ленты постов.

    Args:
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.
    Returns:
        dict: Данные в виде json
    """
    posts_db = await get_all_from_table(object_type=Post, db=db)
    posts=[]
    for post in posts_db:
        post_data = await get_post_view(post_id=post.id, user_id=user_id, db=db)
        posts.append(post_data.get('post'))
    return {'posts':posts}


async def get_post_img_view(image_id: int, db: AsyncSession):
    """
    Отдаёт файл картинки, прикреплённой к посту
    Args:
        image_id (int): id картинки в бд
        db (AsyncSession): Сессия базы данных.
    Returns:
        StreamingResponse: файл картинки
    """
    img_db = await get_object_by_id(object_type=MediaInPost, id=image_id, db=db)
    if not img_db:
        raise HTTPException(status_code=400, detail="Такой картинки не существует!")
    return StreamingResponse(BytesIO(img_db.image), media_type='image/png')


async def get_post_view(post_id: int, user_id: int, db: AsyncSession):
    """
    Возвращает данные в json для просмотра отдельного поста
    Args:
        post_id (int): id поста
        user_id (str): ID пользователя.
        db (AsyncSession): сессия бд
    Returns:
        json - данные поста
    """
    stmt = (
        select(Post)
        .options(
            joinedload(Post.author),
            joinedload(Post.voting_variants).joinedload(VotingVariant.votes),
            joinedload(Post.media),
            joinedload(Post.likes),
            joinedload(Post.comments).joinedload(Comment.author)
        )
        .where(Post.id == post_id)
        # Убираем дубликаты из JOIN (если нужно)
        .execution_options(populate_existing=True)
    )

    result = await db.execute(stmt)
    post_db = result.scalars().first()

    if not post_db:
        raise HTTPException(status_code=404, detail="Post not found")

    # Обработка данных
    post = {
        'id':post_id,
        'author_id': post_db.author.id,
        'author_username': post_db.author.username,
        'text': post_db.text,
        'created_at': post_db.created_at,
        'images_id': [img.id for img in post_db.media],
        'likes_count': len(post_db.likes),
        'liked_status': any(like.author_id == user_id for like in post_db.likes),
        'voting_variants': await process_voting_variants(post_db.voting_variants),
        'comments': [
            {
                'id': comment.id,
                'text': comment.text,
                'author_id': comment.author.id,
                'author_username': comment.author.username,
                'created_at': comment.created_at
            }
            for comment in post_db.comments
        ],
        'comments_count':len(post_db.comments),
    }

    return {'post': post}


async def get_message_img_view(image_id: int, db: AsyncSession):
    """
    Отдаёт файл картинки, прикреплённой к посту
    Args:
        image_id (int): id картинки в бд
        db (AsyncSession): Сессия базы данных.
    Returns:
        StreamingResponse: файл картинки
    """
    img_db = await get_object_by_id(object_type=MediaInMessage, id=image_id, db=db)
    if not img_db:
        raise HTTPException(status_code=400, detail="Такой картинки не существует!")
    return StreamingResponse(BytesIO(img_db.image), media_type='image/png')


async def edit_post_view(data: EditPostData, post_id: int, user_id: int, db: AsyncSession):
    """
    Редактирует пост
    Args:
        post_id (int): id поста
        user_id (int): ID пользователя.
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    post = await get_object_by_id(object_type = Post, id = post_id, db = db)
    if not post:
        raise HTTPException(status_code=400, detail="Такого поста не существует!")
    if post.author_id != user_id:
        raise HTTPException(status_code = 400, detail = "Вы не являетесь автором поста!")
    if data.text:
        post.text = data.text
        await db.commit()
    if data.options!=None:
        old_options = await get_post_voting_variants(post_id = post_id, db = db)
        for option in old_options:
            await delete_object(object = option, db = db)
        await db.commit()
        for option in data.options:
            var = VotingVariant(post_id=post.id, text=option)
            await add_and_refresh_object(var, db)
    return {'status':'ok'}


async def delete_post_view(post_id: int, user_id: int, db: AsyncSession):
    """
    Удаляет пост
    Args:
        post_id (int): id поста
        user_id (int): ID пользователя.
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    post = await get_object_by_id(object_type=Post, id=post_id, db=db)
    if not post:
        raise HTTPException(status_code=400, detail="Такого поста не существует!")
    if post.author_id != user_id:
        raise HTTPException(status_code=400, detail="Вы не являетесь автором поста!")
    await delete_object(object=post, db=db)
    return {'status':'ok'}


async def delete_comment_view(comment_id: int, user_id: int, db: AsyncSession):
    """
    Удаляет комментарий
    Args:
        comment_id (int): id комментария
        user_id (int): ID пользователя.
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    comment = await get_object_by_id(object_type=Comment, id=comment_id, db=db)
    if not Comment:
        raise HTTPException(status_code=400, detail="Такого комментария не существует!")
    if comment.author_id != user_id:
        raise HTTPException(status_code=400, detail="Вы не являетесь автором комментария!")
    await delete_object(object=comment, db=db)
    return {'status': 'ok'}


async def delete_vote_view(post_id: int, user_id: int, db: AsyncSession):
    """
    Удаляет голос пользователя на варианте голосования в посте
    Args:
        post_id (int): id поста
        user_id (int): ID пользователя.
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    result = await db.execute(select(Post).where(Post.id==post_id).options(
        joinedload(Post.voting_variants)
    ))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=400, detail="Такого поста не существует")
    for var in post.voting_variants:
        vote = await get_user_vote(var_id=var.id, user_id=user_id, db=db)
        if vote:
            await delete_object(object=vote, db=db)
    await db.commit()
    return {'status':'ok'}


async def delete_message_view(message_id: int, user_id: int, db: AsyncSession):
    """
    Удаляет сообщение
    Args:
        message_id (int): id варианта голосования
        user_id (int): ID пользователя.
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    message = await get_object_by_id(object_type=Message, id=message_id, db=db)
    if not message:
        raise HTTPException(status_code=400, detail="Такого сообщения не существует")
    if message.author_id != user_id:
        raise HTTPException(status_code=400, detail="Вы не автор сообщения")
    await delete_object(object = message, db=db)
    return {'status': 'ok'}


async def change_avatar_view(uploaded_file: UploadFile, user_id: int, db: AsyncSession):
    """
    Меняет аватарку пользователя
    Args:
        uploaded_file (UploadFile): загруженное изображение
        user_id (int): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    user = await get_object_by_id(object_type=User, id=user_id, db=db)
    file_bytes = await uploaded_file.read()
    user.avatar = file_bytes
    await db.commit()
    return {'status':'ok'}


async def get_avatar_view(another_user_id: int, user_id: int, db: AsyncSession):
    """
    Возвращает аватарку пользователя
    Args:
        another_user_id (int): id пользователя, аватарку которого мы получаем
        user_id (int): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        StreamingResponse - файл аватарки, или None
    """
    user = await get_object_by_id(object_type=User, id = another_user_id, db=db)
    if not user:
        raise HTTPException(status_code=400, detail="Такого юзера не существует")
    if not user.avatar:
        return FileResponse('backend/static/avatar.png')
    return StreamingResponse(BytesIO(user.avatar), media_type='image/png')


async def get_chat_view(recipient_id: int, user_id: int, db: AsyncSession):
    """
    Возвращает данные для страницы чата (массив сообщений)
    Args:
        recipient_id (int): id собеседника
        user_id (int): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - массив сообщений
    """
    recipient = await get_object_by_id(object_type=User, id=recipient_id, db=db)
    if not recipient:
        raise HTTPException(status_code=400, detail="Такого пользователя не существует")
    messages_db = await get_messages_between_two_users(first_user_id=user_id, second_user_id=recipient_id, db=db)
    messages = []
    for message in messages_db:
        messages.append({
            'id':message.id,
            'author_id':message.author_id,
            'text':message.text,
            'created_at':message.created_at,
            'images_id':await get_images_id_for_message(message_id=message.id, db=db)
        })

    return {
        'recipient_id':recipient.id,
        'recipient_username':recipient.username,
        'messages':messages
    }


async def get_votes_view(voting_variant_id: int, user_id: int, db: AsyncSession):
    """
    Возвращает список голосовавших за вариант голосования в посте
    (оптимизированная версия с жадной загрузкой)
    Args:
        voting_variant_id (int): id варианта голосования
        user_id (int): id пользователя (не используется в текущей реализации)
        db (AsyncSession): сессия бд
    Returns:
        dict - список голосовавших
    """
    var = await get_object_by_id(object_type=VotingVariant, db=db)
    if not var:
        raise HTTPException(status_code=400, detail="Такого варианта не существует!")
    votes = await get_votes_on_voting_variant(variant_id=voting_variant_id, db=db)

    return {
        'voted_users': [
            {
                'id': vote.user.id,
                'username': vote.user.username
            }
            for vote in votes
        ]
    }

async def get_users_posts_view(user_id: int, db: AsyncSession):
    """
    Отдаёт данные для отрисовки постов пользователя.

    Args:
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.
    Returns:
        dict: Данные в виде json
    """
    posts_db = await get_user_posts(user_id=user_id, db=db)
    posts=[]
    for post in posts_db:
        post_data = await get_post_view(post_id=post.id, user_id=user_id, db=db)
        posts.append(post_data.get('post'))
    return {'posts':posts}


async def get_my_page_view(user_id: int, db: AsyncSession):
    """
    Возвращает пользователю информацию о нём
    Args:
        user_id (int): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - данные
    """
    user = await get_object_by_id(object_type=User, id=user_id, db=db)
    posts = await get_users_posts_view(user_id=user_id, db=db)
    return {
        'username':user.username,
        'name':user.name,
        'surname':user.surname,
        'email':user.email,
        'posts': posts.get('posts')
    }


async def get_other_page_view(other_user_id: int, user_id: int, db: AsyncSession):
    """
    Возвращает пользователю информацию о нём
    Args:
        user_id (int): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - данные
    """
    user = await get_object_by_id(object_type=User, id=other_user_id, db=db)
    if not user:
        raise HTTPException(status_code=400, detail="Такого юзера не существует!")
    posts = await get_users_posts_view(user_id=other_user_id, db=db)
    return {
        'username':user.username,
        'name':user.name,
        'surname':user.surname,
        'email':user.email,
        'posts': posts.get('posts')
    }


async def get_is_friend_view(friend_id: int, user_id: int, db: AsyncSession):
    """
    Возвращает пользователю, является ли этот человек другом или нет
    Args:
        friend_id_id (int): id пользователя, информацию о котором мы получаем
        user_id (int): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - данные
    """
    friendship = await get_existing_friendship(first_friend_id=friend_id, second_friend_id=user_id, db=db)
    if friendship:
        return {'isFriend':True}
    return {'isFriend':False}


async def get_friends_view(user_id: int, db: AsyncSession):
    """
    Возвращает массив id пользователя
    Args:
        user_id (int): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - данные
    """
    friends_list = await get_user_friends(user_id=user_id, db=db)
    return {
        'friends_list':[
            {
                'id':friend.id,
                'username':friend.username
            }
            for friend in friends_list
        ]
    }


async def delete_friend_view(friend_id: int, user_id: int, db: AsyncSession):
    """
    Удаляет друга
    Args:
        friend_id (int): id друга
        user_id (int): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    friendship = await get_existing_friendship(first_friend_id=friend_id, second_friend_id=user_id, db=db)
    if friendship:
        await delete_object(object=friendship, db=db)
    return {'status':'ok'}


async def get_friendship_requests_view(user_id: int, db: AsyncSession):
    """
    Возвращает запросы дружбы, отправленные пользователю
    Args:
        user_id (str): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - запросы дружбы
    """
    result_db = await get_friendship_requests_for_user(user_id=user_id, db=db)
    return {
        'friendship_requests':[ {
            'id':request.id,
            'author_id':request.author_id,
            'author_username':request.author.username
        }
        for request in result_db.scalars().all() ]
    }


async def delete_friendship_request_view(request_id: int, user_id: int, db: AsyncSession):
    """
    Отклоняет входящий запрос дружбы
    Args:
        request_id (int): id запроса
        user_id (int): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    request = await get_object_by_id(object_type=FriendshipRequest, id=request_id, db=db)
    if not request:
        raise HTTPException(status_code=400, detail="Такого запроса не существует")
    if request.getter_id!=user_id:
        raise HTTPException(status_code=400, detail="Этот запрос направлен не вам")
    await delete_object(object=request, db=db)
    return {'status':'ok'}


async def delete_post_image_view(image_id: int, user_id: int, db: AsyncSession):
    """
    Удаляет изображение прикреплённое к посту
    Args:
        image_id (int): id картинки
        user_id (int): id пользователя
        db (AsyncSession): сессия бд
    Returns:
        json - статус операции
    """
    result = await db.execute(select(MediaInPost).options(
        joinedload(MediaInPost.post)
    ).where(MediaInPost.id == image_id))
    image = result.scalars().first()
    if not image:
        raise HTTPException(status_code=400, detail="Такой картинки не существует!")
    if image.post.author_id!=user_id:
        raise HTTPException(status_code=400, detail="Вы не автор поста!")
    await delete_object(object=image, db=db)
    return {'status':'ok'}


async def complaint_post_view(post_id: int, user_id: int, db: AsyncSession):
    """
    Создание жалобы о посте
    Args:
        post_id (int): id поста
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.
    Returns:
        dict: Статус операции
    """
    post = await get_object_by_id(object_type=Post, id=post_id, db=db)
    
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    new_complaint = ComplaintAboutPost(post_id=post_id, author_id=post.author_id)

    await add_and_refresh_object(object=new_complaint, db=db)
    return {'status': 'ok'}


async def complaint_comment_view(comment_id: int, user_id: int, db: AsyncSession):
    """
    Создание жалобы о комментарии
    Args:
        post_id (int): id поста
        user_id (str): ID пользователя.
        db (AsyncSession): Сессия базы данных.
    Returns:
        dict: Статус операции
    """
    comment = await get_object_by_id(object_type=Comment, id=comment_id, db=db)
    
    if not comment:
        raise HTTPException(status_code=404, detail="Комментарий не найден")

    new_complaint = ComplaintAboutComment(comment_id=comment_id, author_id=comment.author_id)

    await add_and_refresh_object(object=new_complaint, db=db)
    return {'status': 'ok'}