"""
Тут у нас конфигурация для системы авторизации
"""
from authx import AuthX, AuthXConfig
import os


config = AuthXConfig()
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = os.getenv('SECRET_KEY')
config.JWT_ACCESS_COOKIE_NAME = "auth_token_y_py_masters"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False

security = AuthX(config=config)
