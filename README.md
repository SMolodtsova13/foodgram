# Продуктовый помощник Foodgram

### Ссылка на проект: [foodgram](http://foodgram.webhop.me/)

[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=008080)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=008080)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=008080)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=008080)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=008080)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=008080)](https://github.com/features/actions)


## Описание проекта Foodgram
Продуктовый помощник - это сервис, на котором пользователям доступны публиковация рецептов, подписки на публикации других пользователей, добавление понравившиеся рецепты в список «Избранное», а так же выгрузка сводного списка продуктов, необходимых для приготовления одного или нескольких выбранных блюд.  


## Запуск проекта

- Клонируйте репозиторий с проектом на свой компьютер. В терминале из рабочей директории выполните команду:
```
git clone https://github.com/SMolodtsova13/foodgram.git
```

- Установить и активировать виртуальное окружение

```
source /venv/bin/activate
```

- Установить зависимости из файла requirements.txt

```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
- Создать файл .env в папке проекта:
```.env
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
DEBUG=0
```

### Выполните миграции:
```
python manage.py migrate
```

- В папке с файлом manage.py выполнить команду:
```
python manage.py runserver
```

- Создание супер пользователя 
```
python manage.py createsuperuser
```

### Загрузите статику:
```
python manage.py collectstatic --no-input
```
### Заполните базу тестовыми данными: 
```
python manage.py dataloads
```


## Запуск проекта через Docker

Установите Docker, используя инструкции с официального сайта:
- для [Windows и MacOS](https://www.docker.com/products/docker-desktop)
- для [Linux](https://docs.docker.com/engine/install/ubuntu/). Отдельно потребуется установть [Docker Compose](https://docs.docker.com/compose/install/)

Клонируйте репозиторий с проектом на свой компьютер.
В терминале из рабочей директории выполните команду:
```
git clone https://github.com/SMolodtsova13/foodgram.git
```

- в Docker cоздаем образ :
```
docker build -t foodgram .
```

Выполните команду:
```
cd ../infra
docker-compose up -d --build
```

- В результате должны быть собрано три контейнера, при введении следующей команды получаем список запущенных контейнеров:  
```
docker-compose ps
```
Назначение контейнеров:  

|          IMAGES                        | NAMES                |        DESCRIPTIONS         |
|:--------------------------------------:|:---------------------|:---------------------------:|
|       nginx:1.25.4                     | infra-_nginx_1       |   контейнер HTTP-сервера    |
|       postgres:13                      | infra-_db_1          |    контейнер базы данных    |
| smolodtsova13/foodgram_backend:latest  | infra-_backend_1     | контейнер приложения Django |
| smolodtsova13/foodgram_frontend:latest | infra-_frontend_1    | контейнер приложения React  |


### Выполните миграции:
```
docker-compose exec backend python manage.py migrate
```
### Создайте суперпользователя:
```
docker-compose exec backend python manage.py createsuperuser
```

### Загрузите статику:
```
docker-compose exec backend python manage.py collectstatic --no-input
```

### Заполните базу тестовыми данными:
```
docker-compose exec backend python manage.py dataloads
```

## Основные адреса: 

| Адрес                 | Описание |
|:----------------------|:---------|
| 127.0.0.1            | Главная страница |
| 127.0.0.1/admin/     | Для входа в панель администратора |
| 127.0.0.1/api/docs/  | Описание работы API |

## Пользовательские роли
![ Пользовательские роли](https://i.imgur.com/LSv1kca.png)

## Автор:  
_Молодцова Светлана_  
**telegram** _@smolodtsova_
