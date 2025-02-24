from fastapi import FastAPI, Form, APIRouter, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .schemas import *
from backend.db.models import *
from authx import AuthX, AuthXConfig
import os
from .utils import hash_password, verify_password
import asyncio
from sqlalchemy.future import select


config = AuthXConfig()
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = os.getenv('SECRET_KEY')
config.JWT_ACCESS_COOKIE_NAME = "auth_token"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)





async def register_view(data: RegisterFormData, db: Session):
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
