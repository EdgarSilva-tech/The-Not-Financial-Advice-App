import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class DataSource(Base):

    __tablename__ = "DataSources"

    datasource_id = Column("datasource_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    datasource_name = Column("datasource_name", String, unique=True)
    sector_id = Column("sector_id", UUID(as_uuid=True), ForeignKey("Sectors.sector_id"), nullable=False)
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


class DataSourceOutput(Base):

    __tablename__ = "DataSourceOutputs"

    output_id = Column("output_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    datasource_id = Column("datasource_id", UUID(as_uuid=True), ForeignKey("DataSources.datasource_id"), nullable=False)
    pipeline_run_id = Column("pipeline_run_id", String, ForeignKey("Pipelines.pipeline_id"), nullable=False)
    output_key = Column("output_key", String)
    output_type = Column("output_type", String)
    fetched_at = Column("fetched_at", DateTime, default=None)
    expired_at = Column("expired_at", DateTime, default=None)
    status = Column("status", String)

    def __init__(
        self, output_id, datasource_id, pipeline_run_id, 
        output_key, output_type, fetched_at, expired_at, status):

        self.output_id = output_id
        self.datasource_id = datasource_id
        self.pipeline_run_id = pipeline_run_id
        self.output_key = output_key
        self.output_type = output_type
        self.fetched_at = fetched_at
        self.expired_at = expired_at
        self.status = status

    
    def __repr__(self):
        return f"{self.output_id} - {self.pipeline_run_id} - {self.pipeline_run_id} - {self.output_type} - {self.output_key}"


class DataSourcesLink(Base):

    __tablename__="DataSourceLinks"

    link_id = Column("link_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    datasource_id = Column("datasource_id", UUID(as_uuid=True), ForeignKey("DataSources.datasource_id"), nullable=False)
    url = Column("url", String)
    link_type = Column("link_type", String)
    created_at = Column("created_at", DateTime, default=None)

    def __init__(self, link_id, datasource_id, url, link_type, created_at):

        self.link_id = link_id
        self.datasource_id = datasource_id
        self.url = url
        self.link_type = link_type
        self.created_at = created_at

    def __repr__(self):
        return f"{self.link_id} - {self.datasource_id} - {self.url} - {self.link_type} - {self.created_at}"
