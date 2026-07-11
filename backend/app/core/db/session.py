from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from app.models.base import Base

load_dotenv()
POSTGRES_USER=os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT=os.getenv("POSTGRES_PORT")
POSTGRES_DB_NAME=os.getenv("POSTGRES_DB_NAME")
POSTGRES_URL=f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB_NAME}"

engine = create_async_engine(POSTGRES_URL, echo=True)


async def init_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

Session = sessionmaker(bind=engine, class_=AsyncSession)


@asynccontextmanager
async def get_session():
    try:
        async_session = Session()

        async with async_session as session:
            yield session
    except:
        await session.rollback()
        raise
    finally:
        await session.close()
