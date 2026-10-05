from typing import Annotated

from fastapi import Depends

from src.db.connection import sessionmaker
from src.db.manager import DBManager


async def get_db():
    async with DBManager(sessionmaker) as db:
        yield db


# зависимость для проброса DBManager объекта в эндпоинт
DatabaseDep = Annotated[DBManager, Depends(get_db)]
