"""Фабрика для создания async сессий БД."""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.settings import get_settings

settings = get_settings()

# Создаем async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.LOG_LEVEL == "DEBUG",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncSession:
    """Получить async сессию БД.

    Yields:
        AsyncSession: Сессия базы данных
    """
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    """Инициализировать подключение к базе данных."""
    # Проверяем подключение
    async with engine.begin():
        # Можно добавить дополнительную логику инициализации
        pass


async def close_db() -> None:
    """Закрыть подключение к базе данных."""
    await engine.dispose()
