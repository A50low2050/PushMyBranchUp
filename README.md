# PushMyBranchUp

Мини-соцсеть для группы

## Запуск проекта

Для начала нужно создать виртуальное окружение и установить библиотеки.

```bash
# создаём виртуальное окружение
python -m venv .venv
# активируем его
.venv\Scripts\activate
# устанавливаем библиотеки
pip install -r requirements.txt
```

Далее создаём `.env` файл на основе `.env.example`.

```bash
# конфигурация для uvicorn
ENV_UVICORN__HOST=localhost
ENV_UVICORN__PORT=8888
ENV_UVICORN__RELOAD=True

# URL для подключения к SQLite
ENV_DATABASE__URL=sqlite+aiosqlite:///./db.sqlite3
```

Далее нужно установить хуки для утилиты pre-commit, чтобы автоматически проверять код до того, как он будет опубликован в git.

```bash
# устанавливаем хуки для pre-commit
pre-commit install --hook-type pre-commit --hook-type pre-push
# можно вручную запустить хуки
pre-commit run --all-files
```

Сам pre-commit использует статический анализатор mypy и форматтер flake8. Для их запуска можно прописать следующие команды.

```bash
# запустить анализ типов для src/
mypy src/
# проверить формат кода для src/
flake8 src/
```

После всех процедур можно запустить приложение.

```bash
# запускаем приложение
python ./src/main.py
```

## Структура проекта

Проект работает по адресу http://localhost:8888. Документация доступна по адресу `http://localhost:8888/docs/`. Адрес может меняться в зависимости от указанного в конфигурации порта `uvicorn`.
