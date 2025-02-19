from passlib.context import CryptContext
import bcrypt

# Настройка контекста для хэширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Хэширование пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(stored_hashed_password: str, provided_password: str) -> bool:
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hashed_password.encode('utf-8'))