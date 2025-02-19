from fastapi import FastAPI, Form, APIRouter, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import Depends
from application.schemas import *
from db.models import *
from authx import AuthX, AuthXConfig
import os
from application.utils import hash_password, verify_password
import asyncio
from sqlalchemy.future import select

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (для разработки)
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)

config = AuthXConfig()
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = os.getenv('SECRET_KEY')
config.JWT_ACCESS_COOKIE_NAME = "auth_token"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)

async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db

@app.get('/')
async def example():
    return {'ok':'ok'}

@app.post('/register')
async def submit_form(data: RegisterFormData, db: Session = Depends(get_db)): # при некорректном формате данных статус код 422
    result_username = await db.execute(select(User).filter(User.username == data.username))
    db_user_by_username = result_username.scalars().first()
    result_email = await db.execute(select(User).filter(User.email == data.email))
    db_user_by_email = result_email.scalars().first()
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Пользователь с таким юзернеймом уже существует.")
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует.")
    new_user = User(
        username = data.username,
        email = data.email,
        name = data.name,
        surname = data.surname,
        password = hash_password(data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {'status':'ok'}

@app.post('/login')
async def login(data: LoginFormData, response: Response, db: Session = Depends(get_db)):
    result_email = await db.execute(select(User).filter(User.email == data.email))
    db_user_by_email = result_email.scalars().first()
    if not db_user_by_email:
        raise HTTPException(status_code=401, detail="Пользователя с таким email не существует! Зарегистрируйтесь, пожалуйста")
    if not verify_password(db_user_by_email.password, data.password):
        raise HTTPException(status_code=401, detail="Неверный пароль!")
    token = security.create_access_token(uid=str(db_user_by_email.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    print(token)
    return {"auth_token":token}

@app.get('/protected', dependencies = [Depends(security.access_token_required)]) # неавторизованному пользователю вернёт статус код 500
async def secret():
    return {'data':'secret data'}

@app.post('/logout')
async def logout(response: Response):
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    return {"message": "Вы успешно вышли из аккаунта."}

@app.post('/createpost', dependencies = [Depends(security.access_token_required)])
async def create_post():
    pass