# Проект Foodgram, «Продуктовый помощник»

CI/CD foodgram: ![status](https://github.com/ObdulTipov/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## Описание

Foodgram, «Продуктовый помощник». На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Адрес сервиса

**http://62.84.125.111/**

## Доступ к **http://62.84.125.111/admin/**

# email

* rewiwer@yandex.ru

# password

* reviwerpassword

## Ключевые технологии

* Python
* Django
* Djagorestframework
* djoser
* Docker
* docker-compose
* nginx
* gunicorn
* psycopg2-binary
* GitHub Actions

## Установка

1. Cклонируйте репозитарий и создайте копию проекта в своём профиле **github**:

`git clone git@github.com:ObduTipov/foodgram-project-react.git`

2. Установите **docker** и **docker-compose**.
Инструкция по установке можно найти по ссылке **https://docs.docker.com/engine/install/ubuntu/**

3. Из директории **/infra/** скопируйте на сервер docker-compose.yaml и nginx.conf. Это можно сделать, например, по SSH:

```
# scp [путь к файлу] [имя пользователя]@[имя сервера/ip-адрес]:[путь к файлу]. Например:
scp /home/test.txt user@123.123.123.123:/user/home/
```

4. В репозитории проекта на **github** в **Secrets** создайте переменные окружения для работы:

```
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь базы данных postgres>
DB_PASSWORD=<пароль postgres>
DB_HOST=<db>
DB_PORT=<5432>

DOCKER_PASSWORD=<пароль от DockerHub>
DOCKER_USERNAME=<имя пользователя на DockerHub>

SECRET_KEY=<секретный ключ проекта django>

HOST=<IP сервера>
USER=<username для подключения к серверу>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда c терминала **cat ~/.ssh/id_rsa**)>

TELEGRAM_TO=<ID чата, в который придет сообщение>
TELEGRAM_TOKEN=<токен вашего бота>
```

5. С локальной машины выполните команду `git push`. Это запустит CI/CD по файлу **foodrgam_workflow.yml**.
Дождитесь завершения всех задач.

6. Выполните миграции, загрузите статику и подготовленную базу с ингредиентами и тегами, создайте суперпользователя:

```
sudo docker-compose exec -T backend python manage.py makemigrations
sudo docker-compose exec -T backend python manage.py migrate
sudo docker-compose exec -T backend python manage.py collectstatic --no-input
sudo docker-compose exec -T backend python manage.py import_objects
sudo docker-compose exec -T backend python manage.py createsuperuser
```

7. Сервис готов к использованию.
_____________________________________________________

## Авторы

Yandex Practicum, Ivan Meshkov
