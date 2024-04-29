# schemas.py
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

class AdvertisementOut(BaseModel):
    id: int
    title: str
    description: str
    owner_id: int

    class Config:
        orm_mode = True