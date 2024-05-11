from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.models import User, Advertisement
from database import SessionLocal, get_db
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI
from app.routers import router

app = FastAPI(
    title="Web-сервис доски обьявлений",
    description="здесь должно быть какое-либо описание веб-сервиса...",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url=None
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
