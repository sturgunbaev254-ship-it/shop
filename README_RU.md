# Shop API — интернет-магазин на Django REST Framework

## Установка на Windows

Открой терминал в папке, где находится `manage.py`:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations main
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Если venv уже существует, не создавай его повторно — активируй и установи requirements.

## Ссылки

- Товары: http://127.0.0.1:8000/api/products/
- Категории: http://127.0.0.1:8000/api/categories/
- Заказы: http://127.0.0.1:8000/api/orders/
- Отзывы: http://127.0.0.1:8000/api/reviews/
- Swagger: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/
- Админка: http://127.0.0.1:8000/admin/

## Что делает каждый файл

- `core/settings.py` — настройки проекта, приложения, база, авторизация, фильтры, пагинация, email.
- `core/urls.py` — главные URL и Swagger.
- `main/models.py` — таблицы Category, Product, Order, OrderItem и Review.
- `main/serializers.py` — проверка JSON, регистрация, расчёт заказа и email.
- `main/views.py` — обработка API-запросов, авторизация, CRUD, заказы.
- `main/permissions.py` — кто может менять товары и отзывы.
- `main/filters.py` — фильтры по категории и цене.
- `main/urls.py` — Router автоматически создаёт URL для ViewSets.
- `main/admin.py` — модели в админке.

## Postman

### Регистрация — POST `/api/auth/register/`

```json
{"username":"student1","email":"student1@example.com","password":"StrongPass123"}
```

### Вход — POST `/api/auth/login/`

```json
{"username":"student1","password":"StrongPass123"}
```

Скопируй токен из ответа и добавляй в защищённые запросы заголовок:
`Authorization: Token ТВОЙ_ТОКЕН`

### Создать категорию — POST `/api/categories/`
Требуется токен администратора.

```json
{"name":"Смартфоны","description":"Мобильные устройства"}
```

### Создать товар — POST `/api/products/`
Требуется токен администратора. `category` — ID существующей категории.

```json
{"category":1,"name":"POCO F7 Pro","description":"Смартфон","price":"32000.00","stock":5}
```

### Поиск/фильтр — GET

`/api/products/?search=POCO&min_price=20000&max_price=40000&ordering=-price&page=1`

### Создать заказ — POST `/api/orders/`
Требуется токен обычного пользователя. ID товара должен существовать.

```json
{"items":[{"product":1,"quantity":2}]}
```

### Отзыв — POST `/api/reviews/`

```json
{"product":1,"rating":5,"comment":"Хороший товар"}
```

## Термины простыми словами

- Model — таблица базы данных.
- Serializer — проверяет входящие данные и переводит модели в JSON.
- ViewSet — содержит действия API (список, создание, изменение и удаление).
- Router — создаёт URL для ViewSet.
- Permission — проверяет права пользователя.
- FilterSet — фильтрует товары.
- Pagination — делит длинный список на страницы.
- Token — ключ авторизации.
- Swagger — документация API с возможностью выполнять запросы.
- Postman — программа для ручной проверки запросов.

## Важно

Email настроен в консольный режим: письма видны в терминале, реальная почта не отправляется. `DEBUG=True` и учебный секретный ключ нельзя оставлять в production. SQLite подходит для учебного проекта; для реальной нагрузки и конкурентных заказов лучше PostgreSQL. Перед сдачей запусти проект и проверь все запросы.
