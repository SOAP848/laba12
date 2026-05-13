from fastapi import APIRouter

from app.api.admin.router import router as admin_router
from app.api.auth.router import router as auth_router
from app.api.dishes.router import router as dishes_router
from app.api.favorites.router import router as favorites_router
from app.api.orders.router import router as orders_router
from app.api.orders.tracking import router as tracking_router
from app.api.restaurants.router import router as restaurants_router

api_router = APIRouter()

# Подключаем все роутеры
api_router.include_router(auth_router)
api_router.include_router(restaurants_router)
api_router.include_router(dishes_router)
api_router.include_router(orders_router)
api_router.include_router(tracking_router)
api_router.include_router(favorites_router)
api_router.include_router(admin_router)
