from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значения переменной окружения DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Проверка, что переменная окружения была прочитана корректно
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL is not set in the .env file.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Функция для получения базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()