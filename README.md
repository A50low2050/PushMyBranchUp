# PushMyBranchUp (PMBU)

Современная асинхронная социальная сеть на базе **FastAPI**, **SQLAlchemy 2.0** и **Pydantic v2** для публикации идей, постов, комментариев, лайков, подписок и почтовых уведомлений.

---

## Содержание

- [Ключевые возможности](#ключевые-возможности)
- [Технологический стек](#технологический-стек)
- [Развёртывание проекта с нуля](#развёртывание-проекта-с-нуля)
  - [Способ 1: Быстрый старт с помощью Makefile (рекомендуется)](#способ-1-быстрый-старт-с-помощью-makefile-рекомендуется)
  - [Способ 2: Локальное развёртывание вручную (Python / venv)](#способ-2-локальное-развёртывание-вручную-python--venv)
  - [Способ 3: Развёртывание в Docker и Docker Compose](#способ-3-развёртывание-в-docker-и-docker-compose)
- [Интерактивная документация API (Swagger UI)](#интерактивная-документация-api-swagger-ui)
- [Конфигурация и переменные окружения](#конфигурация-и-переменные-окружения)
- [Система уведомлений](#система-уведомлений)
- [Тестирование и проверка качества кода](#тестирование-и-проверка-качества-кода)
- [Справочник команд Makefile](#справочник-команд-makefile)
- [Структура проекта](#структура-проекта)

---

## Ключевые возможности

- **Аутентификация и пользователи**:
  - Регистрация и безопасная авторизация пользователей (хеширование паролей через `bcrypt`).
  - Выдача JWT `access_token` (в теле ответа) и `refresh_token` (в защищённых `HttpOnly` cookie).
  - Механизм ротации refresh-токенов и отзыв токенов при логауте (Blacklist).
- **Публикации (Посты)**:
  - Создание, чтение, редактирование и удаление собственных постов.
  - Постраничная пагинация (`limit` / `offset`).
  - Счётчики лайков и комментариев, флаг `is_liked` для текущего пользователя.
- **Комментарии**:
  - Добавление, просмотр, редактирование и удаление комментариев к публикациям.
- **Лайки**:
  - Быстрое переключение лайка (toggle: поставить / снять).
- **Подписки и персональная лента**:
  - Подписка и отписка от других пользователей.
  - Персональная лента (`/v1/feed`), отображающая публикации только тех авторов, на которых подписан пользователь.
- **Уведомления**:
  - Асинхронная отправка email-уведомлений в фоновом режиме (`BackgroundTasks`) при появлении новых комментариев, лайков, подписчиков и новых публикаций отслеживаемых авторов.
  - **Гибкий переключатель**: возможность полностью отключить систему уведомлений в конфигурации (`ENV_NOTIFICATIONS__ENABLED=false`).
  - **Автоматический fallback**: если подключение к SMTP-серверу не удаётся при старте приложения, сервер не падает с ошибкой, а автоматически переключает систему уведомлений в отключённый режим и продолжает работу.

---

## Технологический стек

- **Python 3.12+ / 3.13**
- **FastAPI** — высокопроизводительный асинхронный веб-фреймворк.
- **SQLAlchemy 2.0 (Async)** + **aiosqlite** — асинхронный ORM и драйвер для SQLite.
- **Alembic** — миграции схемы базы данных.
- **Pydantic v2 & Pydantic-Settings** — строгая валидация схем данных (DTO) и конфигурации через `.env`.
- **PyJWT** + **bcrypt** — JWT-аутентификация и безопасное хеширование паролей.
- **aiosmtplib** — асинхронная отправка сообщений по протоколу SMTP.
- **Pytest** + **pytest-asyncio** + **httpx** — модульные и сквозные интеграционные тесты.
- **Flake8**, **Mypy**, **Black**, **pre-commit** — линтинг, статическая типизация и форматирование кода.
- **Docker** + **Docker Compose** — мультистейдж сборка контейнеров с оптимизацией через `uv`.

---

## Развёртывание проекта с нуля

### Способ 1: Быстрый старт с помощью Makefile (рекомендуется)

Если в вашей системе установлена утилита `make` (Linux, macOS или Windows с Git Bash / GnuWin32):

**Локальный полный запуск (создание env, миграции и запуск):**
```bash
# 1. Клонируем репозиторий и переходим в каталог проекта
git clone https://github.com/A50low2050/PushMyBranchUp.git
cd PushMyBranchUp

# 2. Устанавливаем зависимости в окружение (если ещё не установлены)
pip install -r requirements.txt

# 3. Полный запуск одной командой
make run
```
> Команда `make run` автоматически создаст файлы `.env` и `.env.docker` из шаблонов (если они ещё не созданы), применит все миграции базы данных Alembic и запустит сервер `python src/main.py`.

**Полный запуск через Docker Compose:**
```bash
# Запуск контейнера (автоматически создаст env, соберёт образ и запустит сервис):
make docker-run

# Остановка контейнеров:
make docker-down
```

Приложение запустится и будет доступно по адресу **http://localhost:8888**.

---

### Способ 2: Локальное развёртывание вручную (Python / venv)

#### Шаг 1. Клонирование репозитория

```bash
git clone https://github.com/A50low2050/PushMyBranchUp.git
cd PushMyBranchUp
```

#### Шаг 2. Создание и активация виртуального окружения

- **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
- **Windows (cmd.exe)**:
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate.bat
  ```
- **Linux / macOS**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

#### Шаг 3. Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Шаг 4. Настройка файла переменных окружения (`.env`)

Скопируйте шаблон `.env.example` в `.env`:

- **Windows (PowerShell)**:
  ```powershell
  Copy-Item .env.example .env
  ```
- **Linux / macOS**:
  ```bash
  cp .env.example .env
  ```

Откройте `.env` и при необходимости скорректируйте параметры (секретный ключ, хост/порт uvicorn, SMTP-настройки).  
Если у вас нет рабочего SMTP-сервера для отправки писем, вы можете оставить `ENV_NOTIFICATIONS__ENABLED=True` (сервер автоматически отключит уведомления при недоступности SMTP) либо явно выключить уведомления, установив:
```env
ENV_NOTIFICATIONS__ENABLED=False
```

#### Шаг 5. Применение миграций базы данных

Для создания таблиц в SQLite базе данных примените миграции с помощью Alembic:

```bash
alembic upgrade head
```

#### Шаг 6. Настройка pre-commit хуков (для разработчиков)

```bash
pre-commit install --hook-type pre-commit --hook-type pre-push
```

#### Шаг 7. Запуск приложения

```bash
python src/main.py
```

После старта сервер начнёт принимать запросы по адресу `http://localhost:8888`.

---

### Способ 3: Развёртывание в Docker и Docker Compose

Проект полностью упакован в Docker-контейнер с мультистейдж сборкой.

#### Шаг 1. Проверьте файл окружения для Docker

В репозитории нужно подготовить файл `.env.docker`. Убедитесь, что он содержит необходимые настройки.

```bash
ENV_UVICORN__HOST=0.0.0.0 # слушать все подключения
ENV_UVICORN__PORT=8888
ENV_UVICORN__RELOAD=False

# в docker используем отдельную папку под БД
ENV_DATABASE__URL=sqlite+aiosqlite:///./data/db.sqlite3

ENV_AUTH__SECRET_KEY=lcvnwFQ2td92ARG5wA74fp1DGfevWJ2UAUpAdG9skn8

# уведомления по почте
ENV_NOTIFICATIONS__ENABLED=True
ENV_NOTIFICATIONS__EMAIL__HOST=smtp.gmail.com
ENV_NOTIFICATIONS__EMAIL__PORT=465
ENV_NOTIFICATIONS__EMAIL__USER=your_smtp_user@gmail.com
ENV_NOTIFICATIONS__EMAIL__PASSWORD=your_app_password
ENV_NOTIFICATIONS__EMAIL__FROM_EMAIL=noreply@pushmybranchup.local
```

#### Шаг 2. Сборка и запуск контейнеров

```bash
# Через Makefile:
make docker-up

# Либо стандартной командой docker compose:
docker compose up -d --build
```

Миграции базы данных будут автоматически применены при старте контейнера (`entrypoint.sh`).

#### Шаг 3. Управление контейнером

```bash
# Просмотр логов в реальном времени:
docker compose logs -f

# Остановка контейнеров:
docker compose down
```

---

## Интерактивная документация API (Swagger UI)

После запуска приложения документация Swagger UI доступна по адресу:  
👉 **[http://localhost:8888/docs](http://localhost:8888/docs)** (или другой порт, если переопределён в `.env`).

### Как авторизоваться в Swagger UI:
1. Выполните запрос **`POST /v1/auth/register`** для регистрации нового пользователя.
2. Выполните запрос **`POST /v1/auth/login`**, передав email и пароль. В теле ответа вернётся `access_token`.
3. Нажмите зелёную кнопку **Authorize** в правом верхнем углу страницы Swagger UI.
4. Вставьте полученный токен в поле ввода (**без слова Bearer**) и нажмите **Authorize**.
5. Теперь все защищённые эндпоинты будут выполняться от лица авторизованного пользователя.

---

## Конфигурация и переменные окружения

Конфигурация проекта управляется через библиотеку `pydantic-settings` с префиксом `ENV_` и разделителем вложенности `__`.

| Переменная окружения | Описание | Значение по умолчанию в `.env.example` |
|----------------------|----------|-----------------------------------------|
| `ENV_UVICORN__HOST` | Хост для запуска Uvicorn | `localhost` |
| `ENV_UVICORN__PORT` | Порт сервера Uvicorn | `8888` |
| `ENV_UVICORN__RELOAD` | Автоперезагрузка сервера при изменении кода | `True` |
| `ENV_DATABASE__URL` | Строка подключения к базе данных | `sqlite+aiosqlite:///./db.sqlite3` |
| `ENV_AUTH__SECRET_KEY` | Секретный ключ для подписи JWT токенов | *(сгенерированная строка)* |
| `ENV_NOTIFICATIONS__ENABLED` | **Главный переключатель системы уведомлений** (`True`/`False`) | `True` |
| `ENV_NOTIFICATIONS__EMAIL__HOST` | Хост SMTP сервера | `smtp.gmail.com` |
| `ENV_NOTIFICATIONS__EMAIL__PORT` | Порт SMTP сервера | `465` |
| `ENV_NOTIFICATIONS__EMAIL__USER` | Имя пользователя / email для SMTP | `your_smtp_user@gmail.com` |
| `ENV_NOTIFICATIONS__EMAIL__PASSWORD` | Пароль приложения для SMTP | `your_app_password` |
| `ENV_NOTIFICATIONS__EMAIL__FROM_EMAIL` | Email отправителя | `noreply@pushmybranchup.local` |

---

## Система уведомлений

В проекте реализована модульная система уведомлений на базе шаблона «Стратегия» (`NotificationService` и провайдеры уведомлений).

### Режимы работы:

1. **Включена (`ENV_NOTIFICATIONS__ENABLED=True`)**:
   - При старте приложение выполняет проверку связи с SMTP-сервером (`ping()`).
   - При успешном подключении сервис регистрируется и готов к рассылке.
   - Фоновые задачи (`BackgroundTasks`) отправляют email при действиях: новый комментарий к посту, новый лайк, новая подписка, новая публикация отслеживаемого автора.

2. **Выключена в конфигурации (`ENV_NOTIFICATIONS__ENABLED=False`)**:
   - Приложение **не опрашивает** SMTP-сервер при запуске, ускоряя старт.
   - Уведомления не отправляются; вызовы `notifications.notify()` логируются и безопасно пропускаются без ошибок.

3. **Автоматическое отключение при сбое подключения к SMTP**:
   - Если в конфигурации уведомления включены (`ENV_NOTIFICATIONS__ENABLED=True`), но SMTP-сервер недоступен (нет интернета, неверный логин/пароль, таймаут):
     - Приложение **не прерывает запуск и не падает с ошибкой**. В лог выводится предупреждение, и сервис уведомлений автоматически переводится в выключенное состояние (`NotificationService(enabled=False)`).
     - Приложение продолжает полноценно работать, а отправка уведомлений безопасно пропускается.

---

## Тестирование и проверка качества кода

### Запуск тестов

Тесты написаны с использованием `pytest` и `pytest-asyncio` и разделены на интеграционные и модульные.

```bash
# Запуск всех тестов:
pytest

# Запуск только быстрых модульных тестов:
pytest src/tests/units
```

### Линтинг и форматирование кода

```bash
# Запуск статического анализатора типов mypy и линтера flake8:
flake8 src
mypy src

# Форматирование кода через black:
black src

# Проверка форматирования без изменения файлов:
black --check src

# Ручной запуск всех pre-commit хуков:
pre-commit run --all-files
```

---

## Справочник команд Makefile

| Команда | Описание |
|---------|----------|
| `make help` | Показать список доступных команд |
| `make run` | **Полный запуск локально**: автоматическое создание `.env` и `.env.docker` из шаблонов, применение миграций Alembic и запуск сервера `python src/main.py` |
| `make docker-run` | **Полный запуск в Docker**: автоматическое создание файлов окружения, сборка и запуск контейнеров в фоне через Docker Compose |
| `make docker-down` | Остановка контейнеров Docker Compose (`docker compose down`) |
| `make migrate` | Применить миграции базы данных вручную (`alembic upgrade head`) |
| `make env` | Создать `.env` и `.env.docker` из шаблонов `.example` (если ещё не созданы) |

---

## Структура проекта

```text
pmbu/
├── .env.example                 # Шаблон переменных окружения
├── .env                         # Локальный файл конфигурации (не коммитится в Git)
├── .env.docker                  # Конфигурация для запуска в Docker-контейнере
├── .gitignore                   # Исключения для Git
├── .pre-commit-config.yaml      # Конфигурация pre-commit хуков (flake8, mypy, black)
├── Dockerfile                   # Оптимизированный мультистейдж Dockerfile с использованием uv
├── docker-compose.yaml          # Описание сервисов Docker Compose
├── entrypoint.sh                # Точка входа в контейнере (автоприменение миграций alembic)
├── Makefile                     # Утилита автоматизации типовых задач разработки и деплоя
├── README.md                    # Документация проекта и инструкция по развёртыванию
├── requirements.txt             # Список зависимостей Python
├── setup.cfg                    # Настройки flake8, mypy и black
├── logconfig.json               # Конфигурация логирования (форматтеры, хэндлеры)
├── alembic.ini                  # Конфигурация инструмента миграций Alembic
├── db.sqlite3                   # Файл базы данных SQLite
│
└── src/                         # Исходный код приложения
    ├── main.py                  # Точка входа для локального запуска сервера Uvicorn
    ├── config.py                # Pydantic-настройки приложения (загрузка из .env)
    │
    ├── api/                     # Слой представления (API)
    │   ├── main.py              # Инициализация FastAPI приложения, lifespan и обработчики ошибок
    │   └── v1/
    │       ├── dependencies/    # Зависимости FastAPI (Depends): DB, Cache, Auth, Notifications
    │       ├── errors.py        # Реестр HTTP-ошибок
    │       └── routes/          # Маршруты API:
    │           ├── auth.py      # /v1/auth (регистрация, логин, рефреш, логаут)
    │           ├── users.py     # /v1/users (профиль пользователя, список)
    │           ├── posts.py     # /v1/posts (CRUD постов, пагинация)
    │           ├── comments.py  # /v1/posts/{id}/comments (комментарии)
    │           ├── likes.py     # /v1/posts/{id}/like (лайки)
    │           └── follows.py   # /v1/users/{id}/follow, /v1/feed (подписки и лента)
    │
    ├── db/                      # Работа с базой данных
    │   ├── connection.py        # Инициализация асинхронного engine и sessionmaker SQLAlchemy
    │   └── manager.py           # Менеджер контекста DBManager для транзакций и репозиториев
    │
    ├── migrations/              # Миграции Alembic
    │   ├── env.py               # Конфигурация подключения Alembic к моделям
    │   └── versions/            # Файлы версий миграций
    │
    ├── models/                  # Декларативные ORM модели SQLAlchemy
    │   ├── base.py              # Базовый класс BaseORM
    │   ├── users.py             # Модель пользователя UserORM
    │   ├── posts.py             # Модель поста PostORM
    │   ├── comments.py          # Модель комментария CommentORM
    │   ├── likes.py             # Модель лайка LikeORM
    │   ├── subscriptions.py     # Модель подписки SubscriptionORM
    │   └── tokens.py            # Модель refresh-токенов RefreshTokenORM
    │
    ├── repos/                   # Слой репозиториев (доступ к данным, CRUD)
    │   ├── base.py              # Базовый репозиторий SQLAlchemyRepository
    │   ├── users.py
    │   ├── posts.py
    │   ├── comments.py
    │   ├── likes.py
    │   ├── subscriptions.py
    │   └── tokens.py
    │
    ├── schemas/                 # Pydantic DTO (валидация запросов и ответов)
    │   ├── users.py
    │   ├── posts.py
    │   ├── comments.py
    │   ├── likes.py
    │   ├── subscriptions.py
    │   └── tokens.py
    │
    ├── services/                # Слой бизнес-логики
    │   ├── base.py              # Базовый сервис BaseService
    │   ├── auth.py              # Логика аутентификации и работы с токенами
    │   ├── users.py             # Логика работы с пользователями
    │   ├── posts.py             # Логика постов и отправки уведомлений
    │   ├── comments.py          # Логика комментариев и отправки уведомлений
    │   ├── likes.py             # Логика лайков и отправки уведомлений
    │   └── follows.py           # Логика подписок, ленты и отправки уведомлений
    │
    ├── utils/                   # Сервисы и вспомогательные утилиты
    │   ├── notiserv.py          # Сервис и провайдеры уведомлений (NotificationService, SMTPProvider)
    │   ├── cacheserv.py         # Асинхронный сервис кэширования
    │   ├── hashserv.py          # Сервис хеширования паролей bcrypt
    │   ├── logserv.py           # Конфигурация и получение логгеров
    │   └── exceptions.py        # Иерархия доменных исключений
    │
    └── tests/                   # Набор тестов
        ├── conftest.py          # Фикстуры для интеграционных тестов
        ├── test_auth.py
        ├── test_users.py
        ├── test_posts.py
        ├── test_comments.py
        ├── test_likes.py
        ├── test_follows.py
        ├── test_feed.py
        └── units/               # Модульные тесты сервисов и компонентов
            ├── conftest.py
            ├── test_posts.py
            ├── test_comments.py
            ├── test_likes.py
            └── test_notifications.py
```