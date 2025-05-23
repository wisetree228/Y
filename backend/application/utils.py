"""
Вспомогательные функции, которые используются во view функциях
"""
from typing import Dict
from datetime import datetime
import json
from jose import JWTError, jwt
from passlib.context import CryptContext
import bcrypt
from fastapi import Request, HTTPException, status, WebSocket
from .config import config


# Настройка контекста для хэширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Хэширование пароля
def hash_password(password: str) -> str:
    """
    Хэширует пароль

    Args:
        password (str): пароль
    Returns:
        str - хэш
    """
    return pwd_context.hash(password)

def verify_password(stored_hashed_password: str, provided_password: str) -> bool:
    """
    Сверяет пароль и хэш из бд

    Args:
        stored_hashed_password (str): хэш
        provided_password (str): пароль
    Returns:
        bool - результат проверки
    """
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hashed_password.encode('utf-8'))

async def get_current_user_id(request: Request) -> str:
    """
    Достаёт из файлов куки токен авторизации и дешифрует оттуда id пользователя

    Args:
        request (Request): http request
    Returns:
        str - id в формате строки
    """
    token = request.cookies.get(config.JWT_ACCESS_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен отсутствует",
        )
    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET_KEY,  # Ваш секретный ключ
            algorithms=[config.JWT_ALGORITHM]  # Алгоритм, используемый для подписи токена
        )
        user_id: str = payload.get("sub")
        if not user_id.isdigit():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен",
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось декодировать токен",
        )


async def process_voting_variants(variants) -> list:
    """
    Обрабатывает данные голосования для возврата пользователю (высчитывает процент)
    
    Args:
        variants (list): варианты
    Returns:
        list - в обработанном формате
    """
    if not variants:
        return []

    total_votes = sum(len(variant.votes) for variant in variants)
    return [
        {
            'id': variant.id,
            'text': variant.text,
            'percent': round((len(variant.votes) / total_votes * 100) if total_votes else 0),
            'votes_count':len(variant.votes)
        }
        for variant in variants
    ]


class WebSocketConnectionManager:
    """
    Упрощает обработку websocket-соединений
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}


    async def connect(self, user_id: str, websocket: WebSocket):
        """
        Устанавливает соединение через websocket с
        пользователем

        Args:
            user_id (str): id подключаемого пользователя
            websocket: вебсокет

        Returns:
            None
        """
        await websocket.accept()
        self.active_connections[user_id] = websocket


    def disconnect(self, user_id: str):
        """
        Отключает соединение с через вебсокетом

        Args:
            user_id (str): id отключаемого пользователя
        Returns:
            None
        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]


    async def send_personal_message(self, message_id: int, author_id: str, text: str, user_id: str):
        """
        Отправляет персональное сообщение в формате JSON

        Args:
            author_id: ID отправителя
            text: Текст сообщения
            user_id: ID получателя
        """
        if user_id in self.active_connections:
            message_data = {
                'id':message_id,
                'author_id': author_id,
                'text': text,
                'created_at': datetime.now().isoformat()
            }
            await self.active_connections[user_id].send_text(json.dumps(message_data))
