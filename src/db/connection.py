import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.pool import ConnectionPoolEntry
from sqlalchemy.pool import NullPool

from src.config import settings

_TESTING = os.environ.get("ENV_TESTING", "false").lower() == "true"

engine = create_async_engine(
    os.environ.get("ENV_DATABASE__URL", "sqlite+aiosqlite:///./db.sqlite3"),
    echo=False,
    poolclass=NullPool if _TESTING else None,
)


@event.listens_for(engine.sync_engine, "connect")
def enable_sqlite_foreign_keys(
    dbapi_connection: DBAPIConnection,
    connection_record: ConnectionPoolEntry,
) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


sessionmaker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=settings.database.autocommit,
    autoflush=settings.database.autoflush,
    expire_on_commit=settings.database.expire_on_commit,
)
