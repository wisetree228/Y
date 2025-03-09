from fastapi import FastAPI,UploadFile, File, Request,WebSocket
from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session
#from fastapi import Depends
# from .schemas import *
# from backend.db.models import *
# from authx import AuthX, AuthXConfig
# import os
from .utils import get_current_user_id, WebSocketConnectionManager
from .views import *
from typing import List, Optional

app = FastAPI()

manager = WebSocketConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (для разработки)
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db

@app.get('/')
async def example():
    return {'status':'ok'}

@app.post('/register')
async def submit_form(data: RegisterFormData, response: Response, db: Session = Depends(get_db)): # при некорректном формате данных статус код 422
    return await register_view(data=data, response=response, db=db)

@app.post('/login')
async def login(data: LoginFormData, response: Response, db: Session = Depends(get_db)):
    return await login_view(data=data, response=response, db=db)

@app.get('/get_my_id', dependencies = [Depends(security.access_token_required)]) # неавторизованному пользователю вернёт статус код 500
async def secret(user_id: str = Depends(get_current_user_id)):
    return {'data':int(user_id)}

@app.post('/logout')
async def logout(response: Response):
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    return {"status": "Вы успешно вышли из аккаунта."}

@app.post('/createpost', dependencies = [Depends(security.access_token_required)])
async def create_post(data: CreatePostData, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return await create_post_view(data=data, user_id=int(user_id), db=db)

@app.post('/create_friendship_request/{getter_id}', dependencies = [Depends(security.access_token_required)])
async def create_friendship_request(getter_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return await create_friendship_request_view(author_id=int(user_id), getter_id=getter_id, db=db)

@app.put('/edit_profile', dependencies = [Depends(security.access_token_required)])
async def edit_profile(data: EditProfileFormData, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return await edit_profile_view(data=data, author_id=int(user_id), db=db)

@app.post('/create_comment/{post_id}', dependencies = [Depends(security.access_token_required)])
async def create_comment(data: CreateCommentData, post_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return await create_comment_view(data=data, post_id=post_id, user_id=int(user_id), db=db)

@app.post('/create_like/{post_id}', dependencies = [Depends(security.access_token_required)])
async def create_or_delete_like(post_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return await create_or_delete_like_view(post_id=post_id, user_id=int(user_id), db=db)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await handle_websocket(websocket, user_id, manager)