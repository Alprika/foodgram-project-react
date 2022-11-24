[![Foodgram workflow](https://github.com/Alprika/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg)](https://github.com/Alprika/foodgram-project-react/actions/workflows/yamdb_workflow.yml)

# Продуктовый помощник Foodgram

## Описание проекта Foodgramcd
«Продуктовый помощник»: приложение, где пользователи публикуют рецепты, подписываться на других авторов и добавляют рецепты в избранное. Сервис позволяет создавать список продуктов, которые необходимы для приготовления выбранных блюд.



.env должен содержать:
```python
DB_ENGINE='django.db.backends.postgresql'
DB_NAME=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=db
DB_PORT='5432'
SECRET_KEY=
ALLOWED_HOSTS=
```
## Примеры

Примеры API запросов:

- [GET] - Получить список всех пользователей.
```
/api/users/
```
ответ: 200
```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/?page=4",
  "previous": "http://foodgram.example.org/api/users/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Пупкин",
      "is_subscribed": false
    }
  ]
}
```
- [POST] /api/users/ - Регистрация пользователя.
```
/api/users/
```
запрос:
```
{
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": "Qwerty123"
}
```
ответ: 201
```
{
    "email": "vpupkin@yandex.ru",
    "id": 0,
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин"
}
```

### Весь перечень API доступен в документации.
```url
http://127.0.0.1/api/docs/
```

