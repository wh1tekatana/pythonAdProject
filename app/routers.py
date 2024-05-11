# routers.py
from urllib.request import Request
from fastapi import APIRouter, Depends, HTTPException, Header, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from flask import app
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from .schemas import TokenData, UserBase, UserCreate, UserLogin, Token, AdvertisementBase
from models.models import User, Advertisement
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from dotenv import load_dotenv
import os

# Инициализация нового экземпляра APIRouter
router = APIRouter()

# Инициализация CryptContext и OAuth2PasswordBearer
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

#РЕГИСТРАЦИЯ ПОЛЬЗОВАТЕЛЯ
@router.post("/sign-up", response_model=UserBase)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#АВТОРИЗАЦИЯ .. ВОЗВРАЩАЕТ ТОКЕН
@router.post("/sign-in", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


#ДОБАВИТЬ ОБЬЯВЛЕНИЕ .. ТРЕБУЕТСЯ ТОКЕН
@router.post("/advertisements/", response_model=AdvertisementBase)
def create_advertisement(advertisement: AdvertisementBase, token: str = Header(None), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неавторизованный доступ",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    db_advertisement = Advertisement(
        title=advertisement.title, 
        description=advertisement.description, 
        type=advertisement.type,  # Новое поле типа
        category=advertisement.category,  # Новое поле категории
        price=advertisement.price,  # Новое поле цены
        location=advertisement.location,  # Новое поле локации
        owner_id=user.id
        )
    db.add(db_advertisement)
    db.commit()
    db.refresh(db_advertisement)
    return db_advertisement

#HOME PAGE
@router.get("/")
def main():
    return FileResponse("templates/index.html")


#УДАЛЕНИЕ ОБЬЯВЛЕНИЯ .. УДАЛИТЬ ОБЬЯВЛЕНИЕ МОЖЕТ ТОЛЬКО СОЗДАТЕЛЬ
@router.delete("/advertisements/{advertisement_id}")
def delete_advertisement(
    advertisement_id: int,
    token: str = Header(..., description="Authorization token"),
    db: Session = Depends(get_db)
):
    current_user = get_current_user(token, db)
    advertisement = db.query(Advertisement).filter(Advertisement.id == advertisement_id).first()
    if advertisement is None:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    
    if advertisement.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас нет прав на удаление этого объявления")
    
    db.delete(advertisement)
    db.commit()
    return {"detail": "Объявление успешно удалено"}

#ПОИСК ПОЛЬЗОВАТЕЛЯ
@router.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь  не найден")
    return user

#ПОИСК КОНКРЕТНОГО ОБЬЯВЛЕНИЯ ПО ID
@router.get("/advertisements/{advertisement_id}")
def read_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    advertisement = db.query(Advertisement).filter(Advertisement.id == advertisement_id).first()
    if advertisement is None:
        raise HTTPException(status_code=404, detail="Обьявление не найдено")
    return advertisement

#ПОЛУЧИТЬ СПИСОК ВСЕХ ОБЬЯВЛЕНИЙ
@router.get("/advertisements/")
def read_advertisements(db: Session = Depends(get_db)):
    advertisements = db.query(Advertisement).all()
    return advertisements


#РЕДАКТИРОВАНИЕ ОБЬЯВЛЕНИЙ .. РЕДАКТИРОВАТЬ МОЖЕТ ТОЛЬКО СОЗДАТЕЛЬ .. ТРЕБУЕТСЯ ТОКЕН
@router.put("/advertisements/{advertisement_id}", response_model=AdvertisementBase)
def update_advertisement(
    advertisement_id: int,
    updated_advertisement: AdvertisementBase,
    token: str = Header(..., description="Authorization token"),
    db: Session = Depends(get_db)
):
    current_user = get_current_user(token, db)
    advertisement = db.query(Advertisement).filter(Advertisement.id == advertisement_id).first()
    if advertisement is None:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    
    if advertisement.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="У вас нет прав на редактирование этого объявления")
    
    advertisement.title = updated_advertisement.title
    advertisement.description = updated_advertisement.description
    advertisement.type = updated_advertisement.type  # Новое поле типа
    advertisement.category = updated_advertisement.category  # Новое поле категории
    advertisement.price = updated_advertisement.price  # Новое поле цены
    advertisement.location = updated_advertisement.location
    db.commit()
    db.refresh(advertisement)
    return advertisement


# ПОИСК ОБЬЯВЛЕНИЙ КОНКРЕТНОГО ПОЛЬЗОВАТЕЛЯ
@router.get("/users/{user_id}/advertisements/")
def read_user_advertisements(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    advertisements = db.query(Advertisement).filter(Advertisement.owner_id == user_id).all()
    return advertisements


#ПОИСК ОБЬЯВЛЕНИЯ ПО КЛЮЧЕВЫМ СЛОВАМ
@router.get("/advertisements/search/")
def search_advertisements(query: str, db: Session = Depends(get_db)):
    search = f"%{query}%"
    advertisements = db.query(Advertisement).filter(Advertisement.title.ilike(search)).all()
    return advertisements
