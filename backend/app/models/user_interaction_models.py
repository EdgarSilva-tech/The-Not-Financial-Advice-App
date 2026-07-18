import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import Base
from sqlalchemy.sql import func


class Notification(Base):

    __tablename__="Notifications"

    notification_id = Column("notification_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = Column("user_id", UUID(as_uuid=True), ForeignKey("Users.user_id"), nullable=False)
    notification_text = Column("notification_text", String)
    notification_type = Column("notification_type", String)
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False)
    read_at = Column("read_at", DateTime, default=None)
    error_log = Column("error_log", String)

    def __init__(
        self, notification_id, user_id, notification_text, notification_type,
        created_at, read_at, error_log
    ) -> None:

        self.notification_id = notification_id
        self.user_id = user_id
        self.notification_id = notification_text
        self.notification_type = notification_type
        self.created_at = created_at
        self.read_at = read_at
        self.error_log = error_log

    def __repr__(self) -> str:
        return f"{self.notification_type} - {self.user_id} - {self.notification_type}"


class ChatSession(Base):

    __tablename__="ChatSessions"

    session_id = Column("session_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = Column("user_id", UUID(as_uuid=True), ForeignKey("Users.user_id"), nullable=False)
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_active_at = Column("last_active_at", DateTime, default=None)
    session_status = Column("session_status", String)
    message_count = Column("message_count", Integer)

    def __init__(
        self, session_id, user_id, created_at,
        last_active_at, session_status, message_count) -> None:

        self.session_id = session_id
        self.user_id = user_id
        self.created_at = created_at
        self.last_active_at = last_active_at
        self.session_status = session_status
        self.message_count = message_count

    def __repr__(self) -> str:
        return f"{self.user_id} - {self.last_active_at}"


class ChatMessage(Base):

    __tablename__="ChatMessages"

    message_id = Column("message_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    session_id = Column("session_id", UUID(as_uuid=True), ForeignKey("ChatSessions.session_id"), nullable=False)
    user_id = Column("user_id", UUID(as_uuid=True), ForeignKey("Users.user_id"), nullable=False)
    role = Column("role", String)
    content = Column("content", String)
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False)
    tokens_used = Column("tokens_used", Integer)

    def __init__(
        self, message_id, session_id, user_id, role,
        content, created_at, tokens_used) -> None:
        
        self.message_id = message_id
        self.session_id = session_id
        self.user_id = user_id
        self.role = role
        self.content = content
        self.created_at = created_at
        self.tokens_used = tokens_used

    def __repr__(self) -> str:
        return f"{self.role} - {self.content} - {self.tokens_used}"


class AgentAuditTrail(Base):

    __tablename__="AgentAuditTrail"

    audit_id = Column("audit_id", UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = Column("user_id", UUID(as_uuid=True), ForeignKey("Users.user_id"), nullable=False)
    session_id = Column("session_id", UUID(as_uuid=True), ForeignKey("ChatSessions.session_id"), nullable=False)
    query_text = Column("query_text", String)
    messages_traces = Column("messages_traces", JSONB)
    tool_calls = Column("tool_calls", JSONB)
    evaluation_content = Column("evaluation_content", JSONB)
    total_tokens_used = Column("total_tokens_used", Integer)
    total_latency_ms = Column("total_latency_ms", Integer)
    created_at = Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __init__(
        self, audit_id, user_id, session_id, query_text,
        messages_traces, tool_calls, evaluation_content,
        total_tokens_used, total_latency_ms, created_at) -> None:

        self.audit_id = audit_id
        self.user_id = user_id
        self.session_id = session_id
        self.query_text = query_text
        self.messages_traces = messages_traces
        self.tool_calls = tool_calls
        self.evaluation_content = evaluation_content
        self.total_tokens_used = total_tokens_used
        self.total_latency_ms = total_latency_ms
        self.created_at = created_at

    def __repr__(self) -> str:
        return f"""
        {self.audit_id} - {self.user_id} - {self.session_id} - {self.query_text}
        - {self.messages_traces} - {self.tool_calls} - {self.evaluation_content} -
        {self.total_tokens_used} - {self.total_latency_ms} - {self.created_at}
        """
