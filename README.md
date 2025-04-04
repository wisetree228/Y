# Инструкция по локальному запуску 

1) создать виртуальное окружение:
```commandline
py -m venv venv
```
-для виндовс
```commandline
python3 -m venv venv
```
-для линукса

2) активировать:
```commandline
venv\Scripts\activate
```
-для виндовс

```commandline
source venv/bin/activate
```
-для линукса


3) Создать файл .env и там установить настройки подключения к бд, а также секретный ключ для шифрования JWT токенов при авторизации, пример:
```
POSTGRES_USER=wisetree
POSTGRES_PASSWORD=123456789
POSTGRES_DB=mydb
SECRET_KEY=96683abd8bb109bc25fe27675433a9b6
DATABASE_URL=postgresql+asyncpg://wisetree:123456789@db:5432/mydb
```


4) Поднять докер (на виндовс просто запустите docker desktop, на линуксе выполните команду ```sudo systemctl start docker```)
5) Выполните команду ```docker-compose up --build```
6) Когда докер поднимется, откройте второй терминал и выполните ```docker-compose run --rm app alembic revision --autogenerate -m "New migration"``` а потом ```docker-compose run --rm app alembic upgrade head``` (создание таблиц в бд)
7) Готово! Проект доступен на локальном сервере по адресу http://localhost:3000 (пользовательский фронтенд), к API бэкенда обращатся по http://localhost:8000
