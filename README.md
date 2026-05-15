# Food Delivery Service API

FastAPI веб-приложение для сервиса доставки еды с полным функционалом управления ресторанами, блюдами, заказами и пользователями.
# Выполнил Кривохин Артём Дмитриевич группа 221131:01 Лабораторная работа №12(AI-ассистированная разработка) Вариант 9  сложность повышенная
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
│   │   ├── reviews/           # Отзывы 
│   │   └── admin/             # Админ-панель
│   ├── models/                # Модели БД
│   ├── schemas/               # Схемы Pydantic
│   ├── services/              # Бизнес-логика
│   ├── core/                  # Конфигурация 
│   ├── dependencies/          # Зависимости
│   ├── tasks/                 # Асинхронные задачи Celery 
│   └── tests/                 # Тесты
├── alembic/                   # Миграции 
├── .github/workflows/   
│   └── python-app.yml         # CI/CD
├── docker-compose.yml         # Docker Compose 
├── Dockerfile                 # Docker образ
├── requirements.txt           # Зависимости
├── .env.example               # Шаблон переменных окружения 
├── PROMPT_LOG.md              # Лог промптов
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
- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **PgAdmin**: http://localhost:5050 (admin@admin.com / admin)

Приложение автоматически применяет миграции Alembic при старте.

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

Скопируйте шаблон `.env.example` в `.env` и настройте переменные:

```bash
cp .env.example .env
```

Отредактируйте `.env` (укажите свои значения):

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
# Применение миграций Alembic
alembic upgrade head
```

#### Запуск приложения

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Приложение будет доступно по адресу: http://localhost:8000

#### Запуск Celery worker (для асинхронных задач)

```bash
celery -A app.core.celery.celery_app worker --loglevel=info
```

## API Документация

После запуска доступны:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Новые компоненты

### API для отзывов

Добавлен роутер `/api/reviews/` для управления отзывами на рестораны и блюда. Поддерживает CRUD операции с проверкой прав доступа. Отзыв должен быть привязан либо к ресторану, либо к блюду (но не к обоим одновременно). Валидация рейтинга (1‑5 звёзд) и текста.

Пример запроса:
```bash
POST /api/reviews/
{
  "rating": 5,
  "comment": "Отличный ресторан!",
  "restaurant_id": 1
}
```

### Кэширование с Redis

Реализован клиент Redis в `app/core/cache.py`. Поддерживает операции get, set, delete с TTL. Используется для снижения нагрузки на БД, например, кэширование списка ресторанов.

Пример использования в роутере:
```python
from app.core.cache import redis_cache

cached = redis_cache.get("restaurants:list")
if cached:
    return json.loads(cached)
# иначе загрузить из БД и сохранить в кэш
```

### Асинхронные задачи с Celery

Настроена очередь задач Celery с брокером Redis. Примеры задач в `app/tasks/email_tasks.py`:
- `send_welcome_email` – отправка приветственного письма после регистрации.
- `send_order_confirmation` – отправка подтверждения заказа.

Интеграция с бизнес-логикой: после регистрации пользователя можно вызвать `send_welcome_email.delay(user_email, username)`.

### Слой services

Создана папка `app/services/` для инкапсуляции бизнес-логики. Пример: `restaurant_service.py` содержит методы для работы с ресторанами, отделяя логику от роутеров. Это улучшает тестируемость и поддерживаемость.

### Миграции Alembic

Проект использует Alembic для управления миграциями БД. Начальная миграция `9ebdd3baa85f_initial_migration.py` создаёт все таблицы. При запуске через docker‑compose миграции применяются автоматически. Вручную:

```bash
# Создание новой миграции (после изменения моделей)
alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
alembic upgrade head

# Откат
alembic downgrade -1
```

### Шаблон .env.example

Создан файл `.env.example` с описанием всех необходимых переменных окружения. Используйте его как основу для своего `.env`.

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
- **Тесты граничных значений**: проверка валидации данных (отрицательные цены, пустые списки, минимальные/максимальные значения)

## CI/CD

Проект использует GitHub Actions для автоматизации:
- **Тестирование** при каждом пуше и пул-реквесте
- **Линтинг** кода (black, flake8)

Конфигурация находится в `.github/workflows/python-app.yml`.

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


## Лицензия

MIT
