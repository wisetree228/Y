from pydantic import BaseModel, EmailStr, ValidationError, constr
from datetime import datetime
from typing import List


class RegisterFormData(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)
    password: str

class LoginFormData(BaseModel):
    email: EmailStr
    password: str