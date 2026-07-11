import uuid
from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import asyncio
from dotenv import load_dotenv
import os
from app.models.base import Base


class User(Base):

    __tablename__ = "Users"

    user_id = Column(
        "user_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    username = Column("username", String)
    email = Column("email", String, unique=True)
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

class UserFollowedEntities(Base):

    __tablename__ = "UserFollowedEntities"

    id = Column("id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = Column("user_id", UUID(as_uuid=True), ForeignKey("Users.user_id"))
    entity_id = Column("entity_id", UUID(as_uuid=True), ForeignKey("Entities.entity_id"))
    followed_at = Column("followed_at", DateTime)

    def __init__(self, id, user_id, entity_id, followed_at):
        self.id = id
        self.user_id = user_id
        self.entity_id = entity_id
        self.followed_at = followed_at

    def __repr__(self) -> str:
        return f"{self.id} - {self.user_id} - {self.entity_id} - {self.followed_at}"


class UserPreferredSectors(Base):

    __tablename__ = "UserPreferredSectors"

    id = Column("id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = Column("user_id", UUID(as_uuid=True), ForeignKey("Users.user_id"))
    sector_id = Column("sector_id", UUID(as_uuid=True), ForeignKey("Sectors.sector_id"))
    created_at = Column("created_at", DateTime)

    def __init__(self, id, user_id, sector_id, created_at):
        self.id = id
        self.user_id = user_id
        self.sector_id = sector_id
        self.created_at = created_at

    def __repr__(self) -> str:
        return f"{self.id} - {self.user_id} - {self.sector_id} - {self.followed_at}"
