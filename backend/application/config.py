"""
Тут у нас конфигурация для системы авторизации
"""
from authx import AuthX, AuthXConfig
import os
from datetime import timedelta


config = AuthXConfig()
config.JWT_ALGORITHM = "HS256"
config.JWT_SECRET_KEY = os.getenv('SECRET_KEY')
config.JWT_ACCESS_COOKIE_NAME = "auth_token_y_py_masters"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)

security = AuthX(config=config)
