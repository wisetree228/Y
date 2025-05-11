"""
Схемы для валидации данных
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr, constr, Field


class RegisterFormData(BaseModel):
    """
    Схема валидации данных для формы регистрации
    """
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=2, max_length=50)
    surname: str = Field(min_length=2, max_length=50)
    password: str


class LoginFormData(BaseModel):
    """
    Схема валидации данных для формы логина
    """
    email: EmailStr
    password: str


class CreatePostData(BaseModel):
    """
    Схема валидации данных для формы создания поста
    """
    text: constr(min_length=3, max_length=10000)
    options: Optional[List[constr(min_length=3, max_length=100)]] = None


class EditProfileFormData(BaseModel):
    """
    Схема валидации данных для формы редактирования профиля
    """
    email : Optional[EmailStr] = None
    username: Optional[constr(min_length=3, max_length=10000)] = None
    name: Optional[constr(min_length=2, max_length=10000)] = None
    surname: Optional[constr(min_length=2, max_length=10000)] = None
    password: Optional[str] = None


class CreateCommentData(BaseModel):
    """
    Схема валидации данных для формы комментариев
    """
    text: constr(min_length=3, max_length=10000)


class EditPostData(BaseModel):
    """
    Схема валидации данных для формы редактирования поста
    """
    text: Optional[constr(min_length=3, max_length=10000)] = None
    options: Optional[List[constr(min_length=3, max_length=100)]] = None
