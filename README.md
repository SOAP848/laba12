

# Food Delivery Service API

FastAPI веб-приложение для сервиса доставки еды с полным функционалом управления ресторанами, блюдами, заказами и пользователями.
# Выполнил Кривохин Артём Дмитриевич группа 221131:01 Вариант 9
## Функционал

- **Аутентификация и регистрация** (JWT токены)
- **Управление ресторанами** (CRUD)
- **Управление блюдами** (CRUD)
- **Создание и отслеживание заказов**
- **Трекинг готовности заказа**
- **Избранное** (рестораны и блюда)
- **Отзывы и рейтинги**
- **Админ-панель** для управления контентом
- **Ролевая модель** (клиент, менеджер ресторана, администратор, курьер)

## Технологический стек

- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM
- **PostgreSQL** - база данных
- **Alembic** - миграции
- **Pydantic** - валидация данных
- **JWT** - аутентификация
- **Redis** - кэширование и Celery
- **Docker** - контейнеризация
- **Pytest** - тестирование
- **GitHub Actions** - CI/CD

## Структура проекта

```
food-delivery-api/
├── app/
│   ├── api/                    # Роутеры
│   │   ├── auth/              # Аутентификация
│   │   ├── restaurants/       # Рестораны
│   │   ├── dishes/            # Блюда
│   │   ├── orders/            # Заказы
│   │   ├── favorites/         # Избранное
│   │   └── admin/             # Админ-панель
│   ├── models/                # Модели БД
│   ├── schemas/               # Схемы Pydantic
│   ├── services/              # Бизнес-логика
│   ├── core/                  # Конфигурация
│   ├── dependencies/          # Зависимости
│   └── tests/                 # Тесты
├── alembic/                   # Миграции
├── .github/workflows/         # CI/CD
├── docker-compose.yml         # Docker Compose
├── Dockerfile                 # Docker образ
├── requirements.txt           # Зависимости
└── README.md                  # Документация
```

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/food-delivery-api.git
cd food-delivery-api
```

### 2. Запуск с Docker Compose (рекомендуется)

```bash
docker-compose up -d
```

Сервисы:
- API: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- PgAdmin: http://localhost:5050 (admin@admin.com / admin)

### 3. Ручная установка

#### Требования
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

#### Установка зависимостей

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

#### Настройка окружения

Создайте файл `.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/food_delivery_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379/0
DEBUG=True
```

#### Инициализация базы данных

```bash
# Создание таблиц
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Или с использованием Alembic
alembic upgrade head
```

#### Запуск приложения

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Приложение будет доступно по адресу: http://localhost:8000

## API Документация

После запуска доступны:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Тестирование

### Запуск тестов

```bash
# Все тесты
pytest

# С покрытием кода
pytest --cov=app --cov-report=html

# Конкретный модуль
pytest app/tests/unit/test_models.py -v
```

### Типы тестов

- **Unit-тесты**: тестирование моделей и схем
- **Тесты граничных значений**: проверка валидации данных

## CI/CD

Проект использует GitHub Actions для автоматизации:
- **Тестирование** при каждом пуше и пул-реквесте
- **Линтинг** кода (black, flake8)
- **Сборка Docker образа** при пуше в main
- **Деплой** в продакшн (настраивается)

## Администрирование

### Создание администратора

```python
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    email="admin@example.com",
    username="admin",
    hashed_password=get_password_hash("admin123"),
    role=UserRole.ADMIN,
    is_verified=True
)
db.add(admin)
db.commit()
```

### Доступ к админ-панели

Админ-панель доступна по адресу `/api/admin` (требуются права администратора).

## Миграции базы данных

```bash
# Создание новой миграции
alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

## Развертывание в продакшн

### 1. Настройка переменных окружения

Создайте `.env.production`:

```env
DATABASE_URL=postgresql://user:password@host:5432/production_db
SECRET_KEY=strong-secret-key-from-secrets
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
```

### 2. Сборка и запуск с Docker

```bash
docker build -t food-delivery-api .
docker run -d -p 8000:8000 --env-file .env.production food-delivery-api
```

### 3. Использование Docker Compose для продакшн

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Безопасность

- JWT токены с ограниченным временем жизни
- Хеширование паролей с bcrypt
- Валидация входных данных через Pydantic
- CORS настройки
- Защита от SQL-инъекций через SQLAlchemy
- Ограничение частоты запросов (можно добавить через FastAPI-Limiter)

## Мониторинг и логирование

- Логирование в файл `logs/app.log`
- Health-check эндпоинт `/health`
- Метрики Prometheus (можно добавить через fastapi-prometheus)

## Лицензия

MIT

