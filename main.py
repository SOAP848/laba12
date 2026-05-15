from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.api import api_router
from app.core.database import engine, Base
from app.core.logging import setup_logging

# Настройка логирования
setup_logging()

# Создание таблиц только в режиме разработки (в продакшене — Alembic)
if settings.DEBUG:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Food Delivery Service API",
    description="API для сервиса доставки еды",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Добро пожаловать в сервис доставки еды!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )