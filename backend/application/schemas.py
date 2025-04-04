from pydantic import BaseModel, EmailStr, constr, Field
from typing import List, Optional


class RegisterFormData(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=2, max_length=50)
    surname: str = Field(min_length=2, max_length=50)
    password: str


class LoginFormData(BaseModel):
    email: EmailStr
    password: str


class CreatePostData(BaseModel):
    text: constr(min_length=3, max_length=10000)
    options: Optional[List[constr(min_length=3, max_length=100)]] = None


class EditProfileFormData(BaseModel):
    email : Optional[EmailStr] = None
    username: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    password: Optional[str] = None


class CreateCommentData(BaseModel):
    text: constr(min_length=3, max_length=10000)


class EditPostData(BaseModel):
    text: Optional[constr(min_length=3, max_length=10000)] = None
    options: Optional[List[constr(min_length=3, max_length=100)]] = None


