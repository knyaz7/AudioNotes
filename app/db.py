from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql+asyncpg://postgres:root@db:5432/audionotes"

# Создаем асинхронный движок для подключения к базе данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем асинхронную фабрику сессий для работы с базой данных
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Базовый класс для моделей
Base = declarative_base()


# Получение сессии
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
