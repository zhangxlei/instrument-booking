import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Instrument(TimestampMixin, Base):
    __tablename__ = "instruments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("available", "maintenance", "retired", name="instrument_status", create_type=True),
        nullable=False,
        default="available",
        server_default="available",
    )
    requires_approval: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    max_booking_duration_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=120, server_default="120"
    )
    min_notice_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=60, server_default="60"
    )
    cleanup_time_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=15, server_default="15"
    )
    price_per_hour: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    manager_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    manager_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    probe_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    bookings = relationship("Booking", back_populates="instrument")
    attachments = relationship(
        "InstrumentAttachment", back_populates="instrument", cascade="all, delete-orphan"
    )


class InstrumentMaintenance(TimestampMixin, Base):
    __tablename__ = "instrument_maintenance"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    instrument_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
