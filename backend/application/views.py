from fastapi import FastAPI, Form, APIRouter, Depends, HTTPException, Response, UploadFile, File
from sqlalchemy.orm import Session
from .schemas import *
from backend.db.models import *
from backend.application.utils import hash_password, verify_password
from sqlalchemy.future import select
from .config import config, security





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
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    token = security.create_access_token(uid=str(new_user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {'status': 'ok'}

async def login_view(data: LoginFormData, response: Response, db: Session):
    result_email = await db.execute(select(User).filter(User.email == data.email))
    db_user_by_email = result_email.scalars().first()
    if not db_user_by_email:
        raise HTTPException(status_code=401,
                            detail="Пользователя с таким email не существует! Зарегистрируйтесь, пожалуйста")
    if not verify_password(db_user_by_email.password, data.password):
        raise HTTPException(status_code=401, detail="Неверный пароль!")
    token = security.create_access_token(uid=str(db_user_by_email.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {"auth_token": token}

async def create_post_view(data: CreatePostData, user_id: int, db: Session):
    post = Post(
        text=data.text,
        author_id = user_id
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    if data.options:
        for option in data.options:
            var = VotingVariant(
                post_id = post.id,
                text=option,
            )
            db.add(var)
            await db.commit()
    return {'ok':'ok'}
