.PHONY: help run docker-run docker-up docker-down migrate env

PYTHON ?= python

help:
	@echo Commands:
	@echo   make run         - Setup env, run migrations, and start app locally
	@echo   make docker-run  - Setup env and start app in Docker Compose
	@echo   make docker-up   - Setup env and start app in Docker Compose
	@echo   make docker-down - Stop Docker containers
	@echo   make migrate     - Apply database migrations (alembic upgrade head)
	@echo   make env         - Create .env and .env.docker from templates

env:
	@$(PYTHON) -c "import shutil, pathlib; [print(f'[+] Created {dst} from {src}') if not pathlib.Path(dst).exists() and shutil.copyfile(src, dst) else print(f'[i] {dst} already exists') for src, dst in [('.env.example', '.env'), ('.env.docker.example', '.env.docker')]]"

migrate:
	alembic upgrade head

run: env migrate
	$(PYTHON) src/main.py

docker-run: env
	docker compose up -d --build

docker-up: docker-run

docker-down:
	docker compose down
