from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class AdvertisementBase(BaseModel):
    title: str
    description: str
    type: str  # Новое поле типа
    category: str  # Новое поле категории
    price: str  # Новое поле цены
    location: str  # Новое поле локации

class AdvertisementOut(BaseModel):
    id: int
    title: str
    description: str
    type: str  # Новое поле типа
    category: str  # Новое поле категории
    price: str  # Новое поле цены
    location: str  # Новое поле локации
    owner_id: int

    class Config:
        orm_mode = True