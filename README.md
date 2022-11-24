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
## ## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

git clone https://github.com/.../

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```
Активация в Windows:
```
source env/bin/activate
```
В macOS или Linux:
```
source venv/bin/activate 
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

## Запуск CI/CD

Установить docker, docker-compose на сервере ВМ Yandex.Cloud:
```
ssh username@ip
```
```
sudo apt update && sudo apt upgrade -y && sudo apt install curl -y
```
```
sudo curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && sudo rm get-docker.sh
```
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
```
sudo chmod +x /usr/local/bin/docker-compose
```

Создайтm папку infra:

```
mkdir infra
```
- Перенести файлы docker-compose.yml и default.conf на сервер.

```
scp docker-compose.yml username@server_ip:/home/<username>/infra
```
```
scp default.conf <username>@<server_ip>:/home/<username>/infra
```
- Создайте файл .env в дериктории infra:

```
touch .env
```
- Заполнить в настройках репозитория секреты .env

```python
DB_ENGINE='django.db.backends.postgresql'
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT='5432'
```

Для доступа к контейнеру выполнитm следующие команды:

```
sudo docker-compose exec backend python manage.py makemigrations
```
```
sudo docker-compose exec backend python manage.py migrate --noinput
```
```
sudo docker-compose exec backend python manage.py createsuperuser
```
```
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

Дополнительно можно наполнить базу данных ингредиентами и тэгами:

```
sudo docker-compose exec backend python manage.py load_tags
```
```
sudo docker-compose exec backend python manage.py load_ingredients
```

## Запуск проекта через Docker
- В папке infra выполнить команду, чтобы собрать контейнер:

```
sudo docker-compose up -d
```

Для доступа к контейнеру выполните следующие команды:

```
sudo docker-compose exec backend python manage.py makemigrations
```
```
sudo docker-compose exec backend python manage.py migrate --noinput
```
```
sudo docker-compose exec backend python manage.py createsuperuser
```
```
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

Дополнительно можно наполнить базу данных ингредиентами и тэгами:

```
sudo docker-compose exec backend python manage.py load_tags
```
```
sudo docker-compose exec backend python manage.py load_ingredients
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

