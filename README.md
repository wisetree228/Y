# Проект "Y" | Project "Y"
[Русская версия](#russian-version) | [English Version](#english-version)

<a id="russian-version"></a>
##  Русская версия

### Идея проекта:
Всем известно, что соцсеть "X" (в прошлом "Твиттер") скатилась, и мы решили заменить её самописной соцсетью "Y"

### Сам проект на сервере - http://5.35.126.208/

### Технологический стэк:
#### Backend:
- Python 3.12
- FastAPI 0.115.0
- Postgres
- Alembic 1.13.2
#### Frontend:
- ReactJS
#### Паттерн проектирования на бэкенде - MVC

#### Для поднятия всего проекта используется docker compose

### Реализованный функционал:
- Система регистрации и аутентификации на JWT токенах, которые хранятся в файлах cookie
- Редактирование своего профиля, смена любых данных (инициалов, пароля, аватарки)
- Просмотр чужого профиля, с постами пользователя
- Система дружбы, возможность отправлять и принимать или отклонять запросы добавления в друзья, возможность удалять пользователей из друзей
- Создание постов, редактирование постов, создание голосований и прикрепление картинок в постах, удаление постов
- Лента постов с реализованной пагинацией, рабочими лайками и возможностью голосовать (процентные результаты высчитываются корректно)
- Возможность просмотра отдельных постов, чтения и написания (и, соответственно, удаления) комментариев, возможность посмотреть какие пользователи голосовали за какой вариант голосования
- Работающий в реальном времени без перезагрузки страницы чат между пользователями на вебсокетах, все сообщения сохраняются в бд


# Инструкция по локальному запуску 

1) создать виртуальное окружение:

-для виндовс
```commandline
py -m venv venv
```

-для линукса
```commandline
python3 -m venv venv
```

2) активировать:

-для виндовс
```commandline
venv\Scripts\activate
```

-для линукса
```commandline
source venv/bin/activate
```

3) В корневой директории проекта создать файл .env и там установить настройки подключения к бд, а также секретный ключ для шифрования JWT токенов при авторизации, пример:
```
POSTGRES_USER=wisetree
POSTGRES_PASSWORD=123456789
POSTGRES_DB=mydb
SECRET_KEY=96683abd8bb109bc25fe27675433a9b6
DATABASE_URL=postgresql+asyncpg://wisetree:123456789@db:5432/mydb
```

4) В папке frontend создать ещё один файл .env и записать туда
```
ESLINT_NO_DEV_ERRORS=true
DISABLE_ESLINT_PLUGIN=true
```
(это нужно для отключения ошибок eslint)

5) Поднять докер (на виндовс просто запустите docker desktop, на линуксе выполните команду ```sudo systemctl start docker```)

6) Выполните команду ```sudo docker compose up --build```

7) Когда докер поднимется, откройте второй терминал и выполните ```sudo docker compose run --rm app alembic revision --autogenerate -m "New migration"``` а потом ```sudo docker compose run --rm app alembic upgrade head``` (создание таблиц в бд)

8) Готово! Проект доступен на локальном сервере по адресу http://localhost (пользовательский фронтенд), к API бэкенда обращаться по http://localhost:8000

## Тестирование

Чтобы прогнать тесты с анализом процента покрытия, в корневой директории выполните команду ```pytest --cov=backend```(без созданного по инструкции .env файла в корневой директории тесты работать не будут)

## Генерация документации

1) Перейдите в папку docs (```cd docs```)
2) выполните команду ```make html``` (если не сработало, то ```.\make html```)
3) Теперь, когда документация сгенерирована, откройте в браузере файл который располагается по адресу ```docs/build/html/index.html```

<a id="english-version"></a>
## English version

### Project Idea:
It is well-known that social network "X" (formerly "Twitter") has declined, and we decided to replace it with a custom social network "Y".

### The project is hosted at - http://5.35.126.208/

### Technology Stack:
#### Backend:
- Python 3.12
- FastAPI 0.115.0
- Postgres
- Alembic 1.13.2
#### Frontend:
- ReactJS

#### Design Pattern on the Backend - MVC

#### The entire project is launched using Docker Compose.

### Implemented Functionality:
- User registration and authentication system using JWT tokens stored in cookies.
- Editing user profiles, changing any data (initials, password, avatar).
- Viewing other users' profiles with their posts.
- Friendship system, ability to send and accept or decline friend requests, and remove friends.
- Creating posts, editing posts, creating polls, attaching images to posts, and deleting posts.
- Post feed with implemented pagination, working likes, and voting feature (percentage results are calculated correctly).
- Ability to view individual posts, read and write (and delete) comments, and see which users voted for which poll option.
- Real-time chat between users using WebSockets, with all messages saved in the database.

## Local Launch Instructions

1) Create a virtual environment:

- For Windows
```py -m venv venv```

- For Linux
```python3 -m venv venv```

2) Activate:

- For Windows
```venv\Scripts\activate```

- For Linux
```source venv/bin/activate```

3) In the root directory of the project, create a .env file and set the database connection settings and the secret key for encrypting JWT tokens upon authentication. Example:
```
POSTGRES_USER=wisetree
POSTGRES_PASSWORD=123456789
POSTGRES_DB=mydb
SECRET_KEY=96683abd8bb109bc25fe27675433a9b6
DATABASE_URL=postgresql+asyncpg://wisetree:123456789@db:5432/mydb
```

4) In the frontend folder, create another .env file and write:
```
ESLINT_NO_DEV_ERRORS=true
DISABLE_ESLINT_PLUGIN=true
```

(This is necessary to disable ESLint errors.)

5) Start Docker (on Windows, just launch Docker Desktop; on Linux, execute the command ```sudo systemctl start docker```).

6) Execute the command ```sudo docker compose up --build```.

7) Once Docker is up, open a second terminal and run ```sudo docker compose run --rm app alembic revision --autogenerate -m "New migration"``` and then ```sudo docker compose run --rm app alembic upgrade head``` (this creates tables in the database).

8) Done! The project is available on the local server at http://localhost (user frontend), API backend can be accessed at http://localhost:8000.

## Testing

To run the tests with coverage analysis, in the root directory execute the command ```pytest --cov=backend``` (without the .env file created as per the instructions, the tests will not work).

## Documentation Generation

1) Navigate to the docs folder (```cd docs```).
2) Execute the command ```make html``` (if it doesn't work, try ```.\make html```).
3) Now that the documentation has been generated, open the file located at ```docs/build/html/index.html``` in a browser.



