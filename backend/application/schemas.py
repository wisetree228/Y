from pydantic import BaseModel, EmailStr, ValidationError, constr, Field
from datetime import datetime
from typing import List, Optional
from fastapi import UploadFile


class RegisterFormData(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=2, max_length=50)
    surname: str = Field(min_length=2, max_length=50)
    age: int = Field(gt=18)
    password: str

class LoginFormData(BaseModel):
    email: EmailStr
    password: str

class CreatePostData(BaseModel):
    text: str
    imgs: List[UploadFile] = None
    options: List[str]

class CreateCommentData(BaseModel):
    text: str
    post_id: int


