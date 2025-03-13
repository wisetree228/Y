from fastapi import Response, WebSocket, APIRouter
from .utils import get_current_user_id, WebSocketConnectionManager
from .views import *


router = APIRouter()

manager = WebSocketConnectionManager()


async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        yield db

@router.get('/')
async def example():
    return {'status':'ok'}

@router.post('/register')
async def submit_form(data: RegisterFormData, response: Response, db: Session = Depends(get_db)): # при некорректном формате данных статус код 422
    return await register_view(data=data, response=response, db=db)

@router.post('/login')
async def login(data: LoginFormData, response: Response, db: Session = Depends(get_db)):
    return await login_view(data=data, response=response, db=db)

@router.get('/get_my_id', dependencies = [Depends(security.access_token_required)]) # неавторизованному пользователю вернёт статус код 500
async def secret(user_id: str = Depends(get_current_user_id)):
    return {'data':int(user_id)}

@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie(config.JWT_ACCESS_COOKIE_NAME)
    return {"status": "ok"}

@router.post('/createpost', dependencies = [Depends(security.access_token_required)])
async def create_post(data: CreatePostData, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return await create_post_view(data=data, user_id=int(user_id), db=db)

@router.post('/create_friendship_request/{getter_id}', dependencies = [Depends(security.access_token_required)])
async def create_friendship_request(getter_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return await create_friendship_request_view(author_id=int(user_id), getter_id=getter_id, db=db)

@router.put('/edit_profile', dependencies = [Depends(security.access_token_required)])
async def edit_profile(data: EditProfileFormData, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return await edit_profile_view(data=data, author_id=int(user_id), db=db)

@router.post('/create_comment/{post_id}', dependencies = [Depends(security.access_token_required)])
async def create_comment(data: CreateCommentData, post_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return await create_comment_view(data=data, post_id=post_id, user_id=int(user_id), db=db)

@router.post('/create_like/{post_id}', dependencies = [Depends(security.access_token_required)])
async def create_or_delete_like(post_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return await create_or_delete_like_view(post_id=post_id, user_id=int(user_id), db=db)

@router.post('/vote/{variant_id}', dependencies = [Depends(security.access_token_required)])
async def create_or_delete_like(variant_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return await vote_view(variant_id=variant_id, user_id=int(user_id), db=db)

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, db: Session = Depends(get_db)):
    await handle_websocket(websocket, user_id, manager, db)