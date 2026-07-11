from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from app.models.sector_models import Sector, Entity
from app.models.user_models import User
from app.models.data_models import DataSource
from app.models.user_models import UserFollowedEntities, UserPreferredSectors
import asyncio
from app.models.base import Base
import uuid


load_dotenv()
POSTGRES_USER=os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT=os.getenv("POSTGRES_PORT")
POSTGRES_DB_NAME=os.getenv("POSTGRES_DB_NAME")
POSTGRES_URL=f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB_NAME}"
print(POSTGRES_URL)

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

user_id = uuid.uuid4()
test = User(user_id=user_id, username="Test_User", email="test@email.pt", email_confirmed=False, confirmed_at=None, created_at=None, updated_at=None, risk_tolerance="Low", investment_philosophy_1="Value", investment_philosophy_2="Macro", digest_delivery_day="Tuesday", password_hash="bdygbbcdygdbgycdyg")

async def Test():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with get_session() as session:
        session.add(test)
        await session.commit()

    

asyncio.run(Test())
