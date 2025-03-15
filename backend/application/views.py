from fastapi import FastAPI, Form, APIRouter, Depends, HTTPException, Response, UploadFile, File, WebSocket, WebSocketDisconnect
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from .schemas import *
from backend.db.models import *
from backend.db.utils import *
from backend.application.utils import hash_password, verify_password, WebSocketConnectionManager
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from .config import config, security
import json




async def register_view(data: RegisterFormData, response: Response, db: Session):
    result_username = await db.execute(select(User).filter(User.username == data.username))
    db_user_by_username = result_username.scalars().first()
    result_email = await db.execute(select(User).filter(User.email == data.email))
    db_user_by_email = result_email.scalars().first()
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Пользователь с таким юзернеймом уже существует.")
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует.")
    new_user = User(
        username=data.username,
        email=data.email,
        name=data.name,
        surname=data.surname,
        password=hash_password(data.password)
    )
    await add_and_refresh_object(object=new_user, db=db)
    token = security.create_access_token(uid=str(new_user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {'status': 'ok'}

async def login_view(data: LoginFormData, response: Response, db: Session):
    user = await get_user_by_email(email=data.email, db=db)
    if not user:
        raise HTTPException(status_code=401,
                            detail="Пользователя с таким email не существует! Зарегистрируйтесь, пожалуйста")
    if not verify_password(user.password, data.password):
        raise HTTPException(status_code=401, detail="Неверный пароль!")
    token = security.create_access_token(uid=str(user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"auth_token": token}

async def create_post_view(data: CreatePostData, user_id: int, db: Session):
    post = Post(
        text=data.text,
        author_id = user_id
    )
    await add_and_refresh_object(object=post, db=db)
    if data.options:
        for option in data.options:
            var = VotingVariant(
                post_id = post.id,
                text=option,
            )
            await add_and_refresh_object(object=var, db=db)
    return {'status':'ok'}

async def create_friendship_request_view(author_id: int, getter_id: int, db: Session):
    # Проверка существования получателя
    person = await get_user_by_id(id=getter_id, db=db)
    if not person:
        raise HTTPException(status_code=400, detail="Такого пользователя не существует")


    data_db = await db.execute(select(FriendshipRequest).filter(
        and_(
            FriendshipRequest.author_id == author_id,
            FriendshipRequest.getter_id == getter_id
        )
    ))
    result = data_db.scalars().first()
    if result:
        raise HTTPException(status_code=400, detail="Вы уже отправили этому пользователю запрос дружбы!")

    #Если пользователь отправлял вам запрос дружбы вам до этого, по взаимным запросам создаём дружбу
    data_db = await db.execute(select(FriendshipRequest).filter(
        and_(
            FriendshipRequest.author_id == getter_id,
            FriendshipRequest.getter_id == author_id
        )
    ))
    result1 = data_db.scalars().first()

    data_db = await db.execute(select(Friendship).filter(
        or_(
            and_(Friendship.first_friend_id == author_id, Friendship.second_friend_id == getter_id),
            and_(Friendship.first_friend_id == getter_id, Friendship.second_friend_id == author_id)
        )
    ))
    result = data_db.scalars().first()
    if result:
        raise HTTPException(status_code=400, detail="Вы уже дружите с этим пользователем!")

    if result1:
        new_friendship = Friendship(
            first_friend_id=author_id,
            second_friend_id=getter_id
        )
        await delete_object(obgitject=result1, db=db)
        await add_and_refresh_object(object=new_friendship, db=db)
        return {'status':'you got a new friend!'}

    #Если ничего из вышеперечисленного, создаём новый запрос
    new_request = FriendshipRequest(
        author_id=author_id,
        getter_id = getter_id
    )
    db.add(new_request)
    await db.commit()
    return {'status':'запрос отправлен, ожидайте ответа от пользователя'}

async def edit_profile_view(data: EditProfileFormData, author_id: int, db: Session):
    result_username = await db.execute(select(User).filter(User.username == data.username))
    db_user_by_username = result_username.scalars().first()
    result_email = await db.execute(select(User).filter(User.email == data.email))
    db_user_by_email = result_email.scalars().first()
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Пользователь с таким юзернеймом уже существует.")
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует.")
    data_db  = await db.execute(select(User).filter(User.id == author_id))
    user = data_db.scalars().first()
    if data.username: user.username = data.username
    if data.email: user.email = data.email
    if data.name: user.name = data.name
    if data.surname: user.surname = data.surname
    if data.password: user.password = hash_password(data.password)
    await db.commit()
    await db.refresh(user)
    return {'status':'ok'}

async def create_comment_view(data: CreateCommentData, post_id: int, user_id: int, db: Session):
    post = await get_post_by_id(id=post_id, db=db)
    if not post:
        raise HTTPException(status_code=400, detail="Поста с таким id не существует!")
    comment = Comment(
        text=data.text,
        post_id=post_id,
        author_id=user_id
    )
    await add_and_refresh_object(object=comment, db=db)
    return {'status':'ok'}

async def create_or_delete_like_view(post_id: int, user_id: int, db: Session):
    post =await get_post_by_id(id=post_id, db=db)
    if not post:
        raise HTTPException(status_code=400, detail="Такого поста не существует!")
    like = await get_like_on_post_from_user(post_id=post_id, user_id=user_id, db=db)
    if not like:
        new_like = Like(
            post_id=post_id,
            author_id=user_id
        )
        await add_and_refresh_object(object=new_like, db=db)
        return {'status':'liked', 'likes_count':await get_likes_count(post_id=post_id, db=db)}
    await delete_object(object=like, db=db)
    return {'status':'unliked', 'likes_count':await get_likes_count(post_id=post_id, db=db)}

async def handle_websocket(websocket: WebSocket, user_id: str, manager: WebSocketConnectionManager, db: Session):
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
                await add_and_refresh_object(object=new_message, db=db)
            else:
                await websocket.send_text("Invalid message format")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.send_personal_message(f"User {user_id} left the chat", recipient_id)

async def vote_view(variant_id: int, user_id: int, db: Session):
    var = await db.execute(
        select(VotingVariant)
        .where(VotingVariant.id == variant_id)
        .options(selectinload(VotingVariant.post).selectinload(Post.voting_variants))
    )
    var = var.scalars().first()
    if not var:
        raise HTTPException(status_code=400, detail="Такого варианта голосования не существует!")
    for variant in var.post.voting_variants:
        vote = await get_user_vote(var_id=variant.id, user_id=user_id, db=db)
        if vote:
            await delete_object(object=vote, db=db)
    new_vote = Vote(
        user_id=user_id,
        variant_id=variant_id
    )
    await add_and_refresh_object(object=new_vote, db=db)
    return {'status': 'ok'}

async def add_media_to_post_view(uploaded_file: UploadFile, post_id: int, user_id: int, db: Session):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Пост не найден")

    if post.author_id != user_id:
        raise HTTPException(status_code=403, detail="Вы не являетесь автором поста")
    
    file_bytes = await uploaded_file.read()

    new_media = MediaInPost(post_id=post_id, image=file_bytes)

    await add_and_refresh_object(object=new_media, db=db)
    return {'status': 'file successfully added'}
