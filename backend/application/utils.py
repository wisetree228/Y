from passlib.context import CryptContext
import bcrypt
from .config import config, security
from fastapi import Request, HTTPException, status
from jose import JWTError, jwt

# Настройка контекста для хэширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Хэширование пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(stored_hashed_password: str, provided_password: str) -> bool:
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hashed_password.encode('utf-8'))

async def get_current_user_id(request: Request):
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
            algorithms=[config.ALGORITHM]  # Алгоритм, используемый для подписи токена
        )
        user_id: str = payload.get("sub")
        if user_id is None:
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