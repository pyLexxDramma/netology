# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True # Для SQLAlchemy 1.4+ используйте orm_mode=True
                        # Для SQLAlchemy 2.0+ используйте from_attributes=True

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

class TokenData(BaseModel):
    user_id: int | None = None