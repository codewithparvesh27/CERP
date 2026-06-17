from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Text, Integer, ForeignKey, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.session import Base

class CorrectionSession(Base):
    __tablename__ = "correction_sessions"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_number: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="PENDING_USER_CORRECTION")
    original_request: Mapped[str] = mapped_column(Text)
    original_response: Mapped[str] = mapped_column(Text)
    revised_request: Mapped[str | None] = mapped_column(Text)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class CorrectionWorkItem(Base):
    __tablename__ = "correction_work_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("correction_sessions.id", ondelete="CASCADE"))
    condition_code: Mapped[str] = mapped_column(Text)
    severity_code: Mapped[str | None] = mapped_column(Text)
    disposition_type_code: Mapped[str | None] = mapped_column(Text)
    narrative_text: Mapped[str | None] = mapped_column(Text)
    scope: Mapped[str | None] = mapped_column(Text)
    view_name: Mapped[str | None] = mapped_column(Text)
    section_name: Mapped[str | None] = mapped_column(Text)
    ui_field_name: Mapped[str | None] = mapped_column(Text)
    ui_label: Mapped[str | None] = mapped_column(Text)
    record_id: Mapped[str | None] = mapped_column(Text)
    request_line_number: Mapped[int | None] = mapped_column(Integer)
    request_line_no: Mapped[str | None] = mapped_column(Text)
    field_name: Mapped[str | None] = mapped_column(Text)
    field_start: Mapped[int | None] = mapped_column(Integer)
    field_end: Mapped[int | None] = mapped_column(Integer)
    current_value: Mapped[str | None] = mapped_column(Text)
    corrected_value: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, default="PENDING")
    raw_response_context: Mapped[dict] = mapped_column(JSON, default=list)
    raw_response_condition: Mapped[dict] = mapped_column(JSON, default=dict)
    validation: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("correction_sessions.id", ondelete="CASCADE"))
    work_item_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("correction_work_items.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(Text)
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
