# from fastapi import FastAPI, Form, APIRouter, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session
# from fastapi import Depends
# from .schemas import *
# from backend.db.models import *
# from authx import AuthX, AuthXConfig
# import os
from .utils import get_current_user_id
from .views import *
# import asyncio
# from sqlalchemy.future import select

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (для разработки)
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)

async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db

@app.get('/')
async def example():
    return {'ok':'ok'}

@app.post('/register')
async def submit_form(data: RegisterFormData, response: Response, db: Session = Depends(get_db)): # при некорректном формате данных статус код 422
    return await register_view(data, response, db)

@app.post('/login')
async def login(data: LoginFormData, response: Response, db: Session = Depends(get_db)):
    return await login_view(data, response, db)

@app.get('/protected', dependencies = [Depends(security.access_token_required)]) # неавторизованному пользователю вернёт статус код 500
async def secret(user_id: str = Depends(get_current_user_id)):
    return {'data':user_id}

@app.post('/logout')
async def logout(response: Response):
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    return {"message": "Вы успешно вышли из аккаунта."}

@app.post('/createpost', dependencies = [Depends(security.access_token_required)])
async def create_post():
    pass