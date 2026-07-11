import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class Sector(Base):
    __tablename__ = "Sectors"

    sector_id = Column(
        "sector_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    sector_name = Column(
        "sector_name", String
    )
    sector_description = Column(
        "sector_description", String
    )
    associated_pipeline = Column(
        "associated_pipeline", UUID(as_uuid=True), ForeignKey("DataSources.datasource_id")
    )

    def __init__(self, sector_id, sector_name, sector_description, associated_pipeline):
        
        self.sector_id = sector_id
        self.sector_name = sector_name
        self.sector_description = sector_description
        self.associated_pipeline = associated_pipeline

    def __repr__(self):
        return f"{self.sector_id} - {self.sector_name} - {self.sector_description} - {self.associated_pipeline}"


class Entity(Base):
    __tablename__ = "Entities"

    entity_id = Column(
        "entity_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    entity_name = Column(
        "entity_name", String
    )
    ticker_symbol = Column(
        "ticker_symbol", String
    )
    exchange = Column(
        "exchange", String
    )
    entity_sector = Column(
        "entity_sector", UUID(as_uuid=True), ForeignKey("Sectors.sector_id")
    )
    entity_description = Column(
        "entity_description", String
    )
    entity_type = Column(
        "entity_type", String
    )
    entity_status = Column(
        "entity_status", String
    )

    def __init__(self, entity_id, entity_name, ticker_symbol, exchange, entity_sector, entity_description, entity_type, entity_status):

        self.entity_id = entity_id
        self.entity_name = entity_name
        self.ticker_symbol = ticker_symbol
        self.exchange = exchange
        self.entity_sector = entity_sector
        self.entity_description = entity_description
        self.entity_type = entity_type
        self.entity_status = entity_status
    
    def __repr__(self):
        return f"{self.entity_id} - {self.entity_name} - {self.ticker_symbol} - {self.exchange}"