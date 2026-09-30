from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MarinaSettings(Base):
    __tablename__ = "marina_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    marina_id: Mapped[int] = mapped_column(ForeignKey("marinas.id"), nullable=False, unique=True, index=True)
    office_email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    office_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    emergency_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    vhf_channel: Mapped[str | None] = mapped_column(String(40), nullable=True)
    opening_hours: Mapped[str | None] = mapped_column(Text, nullable=True)
    check_in_start: Mapped[str | None] = mapped_column(String(20), nullable=True)
    check_in_end: Mapped[str | None] = mapped_column(String(20), nullable=True)
    check_out_time: Mapped[str | None] = mapped_column(String(20), nullable=True)
    booking_terms: Mapped[str | None] = mapped_column(Text, nullable=True)
    rules_pdf_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    map_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    nautical_access_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    seabed_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    accepts_catamarans: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    accepts_multihulls: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    marina = relationship("Marina", back_populates="settings")
