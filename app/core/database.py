import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
        
async def wait_for_db():
    for i in range(10):
        try:
            async with engine.connect() as conn:
                return
        except OperationalError:
            print(f"⏳ Waiting for DB... ({i+1}/10)")
            await asyncio.sleep(2)
    raise Exception("Database not ready after waiting")
