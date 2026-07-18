import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base
from sqlalchemy.sql import func


class Document(Base):
    
    __tablename__="Documents"

    document_id = Column("document_id", UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True)
    title = Column("title", String)
    document_type = Column("document_type", String)
    date_sent = Column("date_sent", DateTime, default=None)
    object_storage_key = Column("object_storage_key", String)
    request_user = Column("request_user", UUID(as_uuid=True), ForeignKey("Users.user_id"), nullable=False)
    delivery_status = Column("delivery_status", String)
    error_log = Column("error_log", String)
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __init__(
        self, document_id, title, document_type, date_sent, object_storage_key,
        request_user, delivery_status, error_log, created_at
    ) -> None:

        self.document_id = document_id
        self.title = title
        self.document_type = document_type
        self.date_sent = date_sent
        self.object_storage_key = object_storage_key
        self.request_user = request_user
        self.delivery_status = delivery_status
        self.error_log = error_log
        self.created_at = created_at

    def __repr__(self) -> str:
        return f"{self.title} - {self.document_type} - {self.date_sent} - {self.request_user} - {self.delivery_status}"

class DocumentTag(Base):

    __tablename__="DocumentTags"

    id = Column("id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    document_id = Column("document_id", UUID(as_uuid=True), ForeignKey("Documents.document_id"), nullable=True)
    tag = Column("tag", String)

    def __init__(self, id, document_id, tag) -> None:
        
        self.id = id
        self.document_id = document_id
        self.tag = tag

    def __repr__(self, id, document_id, tag) -> str:
        return f"{self.id} - {self.document_id} - {self.tag}"

        