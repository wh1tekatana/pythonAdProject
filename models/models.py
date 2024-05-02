# models/models.py
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now())

class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    owner_id = Column(Integer)
    type = Column(String)  # Новое поле типа
    category = Column(String)  # Новое поле категории
    price = Column(String)  # Новое поле цены
    location = Column(String)  # Новое поле локации
    created_at = Column(DateTime, server_default=func.now())