import uuid
from datetime import datetime
from typing import ClassVar

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Booking(TimestampMixin, Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    instrument_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("instruments.id"), nullable=False, index=True
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("pending", "approved", "rejected", "cancelled", "completed",
             name="booking_status", create_type=True),
        nullable=False,
        default="pending",
        server_default="pending",
    )
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    probe_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    user = relationship("User", back_populates="bookings", foreign_keys=[user_id])
    approver = relationship("User", back_populates="approved_bookings", foreign_keys=[approved_by])
    instrument = relationship("Instrument", back_populates="bookings")

    # Transient fields (not persisted, populated at query time)
    user_username: ClassVar[str | None] = None
    user_full_name: ClassVar[str | None] = None
    instrument_name: ClassVar[str | None] = None
