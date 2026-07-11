import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class DataSource(Base):

    __tablename__ = "DataSources"

    datasource_id = Column("datasource_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    datasource_name = Column("datasource_name", String, unique=True)
    sector_id = Column("sector_id", UUID(as_uuid=True), ForeignKey("Sectors.sector_id"))
    output_type = Column("output_type", String)
    created_at = Column("created_at", DateTime)

    def __init__(self, datasource_id, datasource_name, sector_id, output_type, created_at):

        self.datasource_id = datasource_id
        self.datasource_name = datasource_name
        self.sector_id = sector_id
        self.output_type = output_type
        self.created_at = created_at

    
    def __repr__(self):
        return f"{self.datasource_id} - {self.datasource_name} - {self.sector_id} - {self.output_type} - {self.created_at}"


