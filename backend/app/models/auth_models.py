import uuid
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
POSTGRES_USER=os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD")
POSTGRES_PORT=os.getenv("POSTGRES_PORT")
POSTGRES_DB_NAME=os.getenv("POSTGRES_DB_NAME")
Base = declarative_base()


class User(Base):

    __tablename__ = "Users"

    user_id = Column(
        "user_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    username = Column("username", String)
    email = Column("email", String)
    email_confirmed = Column("email_confirmed", Boolean, default=False)
    confirmed_at = Column("confirmed_at", DateTime, default=None)
    created_at = Column("created_at", DateTime, default=None)
    updated_at = Column("updated_at", DateTime, default=None)
    risk_tolerance = Column("risk_tolerance", String)
    investment_philosophy_1 = Column("investment_philosophy_1", String)
    investment_philosophy_2 = Column("investment_philosophy_2", String)
    digest_delivery_day = Column("digest_delivery_day", String)
    password_hash = Column("password_hash", String)

    def __init__(
        self, user_id, username, email, email_confirmed, confirmed_at,
        created_at, updated_at, risk_tolerance, investment_philosophy_1,
        investment_philosophy_2, digest_delivery_day, password_hash
    ):

        self.user_id = user_id
        self.username = username
        self.email = email
        self.email_confirmed = email_confirmed
        self.confirmed_at = confirmed_at
        self.created_at = created_at
        self.updated_at = updated_at
        self.risk_tolerance = risk_tolerance
        self.investment_philosophy_1 = investment_philosophy_1
        self.investment_philosophy_2 = investment_philosophy_2
        self.digest_delivery_day = digest_delivery_day
        self.password_hash = password_hash

    def __repr__(self):
        return f"{self.user_id} - {self.username} - {self.risk_tolerance}"


engine = create_async_engine(f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:{POSTGRES_PORT}/{POSTGRES_DB_NAME}", echo=True)


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
