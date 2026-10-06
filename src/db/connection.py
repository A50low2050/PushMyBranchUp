from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

engine = create_async_engine(
    url=settings.database.url,
    echo=settings.database.echo,
)

sessionmaker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=settings.database.autocommit,
    autoflush=settings.database.autoflush,
    expire_on_commit=settings.database.expire_on_commit,
)
