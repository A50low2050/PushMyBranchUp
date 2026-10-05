from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # код до запуска приложения
    yield
    # код после завершения работы приложения


app = FastAPI(
    lifespan=lifespan,
    title=settings.fastapi.name,
    description=settings.fastapi.description,
    root_path=settings.fastapi.root_path,
)
