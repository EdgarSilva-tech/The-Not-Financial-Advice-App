import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class Pipeline(Base):

    __tablename__="Pipelines"

    pipeline_id = Column("pipeline_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    pipeline_def_id = Column("pipeline_def_id", UUID(as_uuid=True), ForeignKey("PipelineDefinitions.pipeline_def_id"), nullable=False)
    run_status = Column("run_status", String)
    run_error_log = Column("run_error_log", String)
    data_source_id = Column("data_source_id", UUID(as_uuid=True), ForeignKey("DataSources.datasource_id"), nullable=False)
    start_time = Column("start_time", DateTime, default=None)
    end_time = Column("end_time", DateTime, default=None)

    def __init__(
        self, pipeline_id, pipeline_def_id, run_status,
        run_error_log, data_source_id, start_time, end_time):

        self.pipeline_id = pipeline_id
        self.pipeline_def_id = pipeline_def_id
        self.run_status = run_status
        self.run_error_log = run_error_log
        self.data_source_id = data_source_id
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self) -> str:
        return f"{self.pipeline_id} - {self.pipeline_def_id} - {self.run_status} - {self.data_source_id} - {self.start_time} - {self.end_time}"


class PipelineDefinition(Base):
    __tablenames__="PipelineDefinitions"

    pipeline_def_id = Column("pipeline_def_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    pipeline_name = Column("pipeline_name", String, nullable=False)
    pipeline_type = Column("pipeline_type", String)
    sector_id = Column("sector_id", UUID(as_uuid=True), ForeignKey("Sectors.sector_id"), nullable=False)
    cadence = Column("cadence", String)
    created_at = Column("created_at", DateTime, default=None)

    def __init__(
        self, pipeline_def_id, pipeline_name, pipeline_type,
        sector_id, cadence, created_at):

        self.pipeline_def_id = pipeline_def_id
        self.pipeline_name = pipeline_name
        self.pipeline_type = pipeline_type
        self.sector_id = sector_id
        self.cadence = cadence
        self.created_at = created_at

    def __repr__(self) -> str:
        return f"{self.pipeline_def_id} - {self.pipeline_name} - {self.pipeline_type} - {self.sector_id} - {self.cadence} - {self.created_at}"


class PipelineCheckpoint(Base):
    __tablenames__="PipelineCheckpoint"

    checkpoint_id = Column("checkpoint_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    pipeline_id = Column("pipeline_id", UUID(as_uuid=True), ForeignKey("Pipelines.pipeline_id"), nullable=False)
    batch_sequence = Column("batch_sequence", Integer)
    checkpoint_status = Column("checkpoint_status", Integer)
    created_at = Column("created_at", DateTime, default=None)
    batch_error_log = Column("batch_error_log", String)

    def __init__(
        self, checkpoint_id, pipeline_id, batch_sequence,
        checkpoint_status, created_at, batch_error_log):

        self.checkpoint_id = checkpoint_id
        self.pipeline_id = pipeline_id
        self.batch_sequence = batch_sequence
        self.checkpoint_status = checkpoint_status
        self.created_at = created_at
        self.batch_error_log = batch_error_log

    def __repr__(self) -> str:
        return f"{self.checkpoint_id} - {self.pipeline_id} - {self.batch_sequence} - {self.checkpoint_status} - {self.created_at} - {self.batch_error_log}"
