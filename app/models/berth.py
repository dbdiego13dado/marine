from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BerthSlot(Base):
    __tablename__ = "berth_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    marina_id: Mapped[int] = mapped_column(ForeignKey("marinas.id"), nullable=False, index=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("marina_zones.id"), nullable=True, index=True)
    code: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    max_length_m: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    max_beam_m: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    max_draft_m: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(40), nullable=False, default="other")
    usage_type: Mapped[str] = mapped_column(String(40), nullable=False, default="transient", index=True)
    price_per_day: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    price_per_week: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    price_per_month: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="available", index=True)
    special_approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    marina = relationship("Marina", back_populates="berth_slots")
    zone = relationship("MarinaZone", back_populates="berths")
    bookings = relationship("Booking", back_populates="berth_slot")
    positions = relationship("BerthPosition", back_populates="berth_slot")
