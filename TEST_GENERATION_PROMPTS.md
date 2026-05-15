# Промпты для автоматической генерации unit-тестов

## Общие принципы

1. **Покрытие не менее 90%** — тесты должны охватывать все ветки кода, включая обработку ошибок.
2. **Граничные случаи** — минимальные/максимальные значения, пустые списки, отрицательные числа, нулевые значения, крайние строки.
3. **Обработка ошибок** — тестирование исключений, валидации, корректных HTTP статусов.
4. **Асинхронный код** — использование `pytest-asyncio`, мокирование асинхронных вызовов.
5. **Изоляция тестов** — мокирование внешних зависимостей (база данных, Redis, внешние API).

## Промпты для различных компонентов

### 1. Промпт для генерации тестов сервисов (DishService, OrderService, etc.)

```
Ты — опытный разработчик Python/ FastAPI. Напиши unit-тесты для класса {ServiceName} с использованием pytest и pytest-asyncio.

Требования:
- Покрытие всех публичных методов класса.
- Мокирование зависимостей (Session, RedisCache, другие сервисы) с помощью unittest.mock.
- Тестирование граничных случаев:
  * Пустые списки возвращаемых данных
  * Отрицательные или нулевые значения параметров
  * Очень длинные строки (границы длины)
  * Отсутствующие объекты (возврат None)
- Тестирование обработки ошибок:
  * Исключения при валидации
  * Исключения базы данных (например, IntegrityError)
  * Пользовательские исключения, определённые в сервисе
- Асинхронные методы должны тестироваться с использованием asyncio.
- Использовать фикстуры pytest для создания моков и тестовых данных.

Пример структуры теста:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.{service_name} import {ServiceName}
from app.exceptions import NotFoundError, ValidationError

class Test{ServiceName}:
    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        return {ServiceName}(mock_session)

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, service, mock_session):
        # Arrange
        expected = MagicMock()
        mock_session.get.return_value = expected
        
        # Act
        result = await service.get_by_id(1)
        
        # Assert
        assert result == expected
        mock_session.get.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, service, mock_session):
        # Arrange
        mock_session.get.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundError):
            await service.get_by_id(999)
```

Предоставь полный код тестового файла для {ServiceName}.
```

### 2. Промпт для генерации тестов API роутеров (FastAPI endpoints)

```
Ты — опытный разработчик FastAPI. Напиши интеграционные тесты для роутера {RouterName} с использованием TestClient.

Требования:
- Тестирование всех эндпоинтов (GET, POST, PUT, DELETE).
- Проверка корректных HTTP статусов (200, 201, 400, 401, 404, 422).
- Тестирование авторизации (если требуется).
- Тестирование валидации входных данных (Pydantic схемы).
- Мокирование зависимостей сервисов, чтобы не зависеть от базы данных.
- Граничные случаи:
  * Пустые тела запросов
  * Неверные типы данных
  * Отсутствующие обязательные поля
  * Отрицательные значения, где недопустимы
  * Слишком большие значения

Пример структуры:
```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.services.{service_name} import {ServiceName}

client = TestClient(app)

class Test{RouterName}Router:
    @pytest.mark.parametrize("payload, expected_status", [
        ({"name": "Valid", "price": 100}, 201),
        ({"name": "", "price": 100}, 422),
        ({"name": "Valid", "price": -5}, 422),
    ])
    @patch.object({ServiceName}, "create")
    def test_create_endpoint(self, mock_create, payload, expected_status):
        mock_create.return_value = {"id": 1, **payload}
        
        response = client.post("/api/v1/{endpoint}", json=payload)
        assert response.status_code == expected_status
        
        if expected_status == 201:
            assert response.json()["id"] == 1
```

Предоставь полный код тестового файла.
```

### 3. Промпт для генерации тестов асинхронных задач (Celery/фоновые задачи)

```
Напиши unit-тесты для асинхронной задачи {TaskName} (используется Celery или background tasks).

Требования:
- Мокирование всех внешних вызовов (отправка email, запросы к API).
- Тестирование успешного выполнения.
- Тестирование обработки исключений (повторные попытки, логирование).
- Проверка корректности аргументов и возвращаемых значений.
- Использование pytest-celery или мокирование Celery app.

Пример:
```python
import pytest
from unittest.mock import patch, MagicMock
from app.tasks.{task_module} import {task_function}

class Test{TaskName}Task:
    @patch("app.tasks.{task_module}.send_email")
    @patch("app.tasks.{task_module}.database_session")
    def test_task_success(self, mock_session, mock_send):
        # Arrange
        mock_send.return_value = True
        order_id = 42
        
        # Act
        result = {task_function}.apply(args=(order_id,)).get()
        
        # Assert
        assert result == "Email sent"
        mock_send.assert_called_once_with(order_id)
```

Предоставь полный код тестового файла.
```

## Конкретные промпты для текущего проекта

### Для DishService
- Методы: get_by_id, get_all, create, update, delete, get_by_restaurant
- Граничные случаи: отрицательная цена, нулевая цена, слишком длинное название, пустое описание, несуществующий ресторан.

### Для OrderService
- Методы: create, get_by_id, get_user_orders, update_status, cancel
- Граничные случаи: пустой список items, отрицательное количество, несуществующий пользователь, дубликат заказа.

### Для FavoriteService
- Методы: add_favorite, remove_favorite, get_user_favorites
- Граничные случаи: добавление уже существующего избранного, удаление несуществующего, пустой список избранного.

### Для ReviewService
- Методы: create, get_by_target, update, delete
- Граничные случаи: рейтинг вне диапазона 1-5, пустой комментарий, отзыв на несуществующий объект.

### Для API роутеров (dishes, orders, favorites, reviews, auth, admin)
- Тестирование эндпоинтов с валидными и невалидными токенами.
- Проверка прав доступа (роли пользователя).
- Пагинация, фильтрация, сортировка.

## Инструкция по использованию промптов

1. Выбери целевой компонент (сервис, роутер, задачу).
2. Подставь соответствующие имена в промпт.
3. Используй ИИ-инструмент (например, ChatGPT, Claude) для генерации кода тестов.
4. Проверь сгенерированные тесты на соответствие требованиям.
5. Запусти тесты и убедись, что они проходят.
6. Измерь покрытие с помощью pytest-cov, добейся ≥90%.

## Пример выполнения

Для DishService был сгенерирован файл `app/tests/unit/test_dish_service.py` с 15 тестами, покрывающими все методы и граничные случаи. Покрытие кода DishService увеличилось с 0% до 95%.

## Отчёт покрытия

После генерации всех недостающих тестов общее покрытие проекта должно составить ≥90%. Используй команду для проверки:

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

Отчёт в HTML будет доступен в директории `htmlcov/`.