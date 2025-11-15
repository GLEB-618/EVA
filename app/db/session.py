from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=False,
)

session_factory = async_sessionmaker(engine)


class Base(DeclarativeBase):
    pass
