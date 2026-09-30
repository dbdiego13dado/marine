from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    marina_id: Mapped[int] = mapped_column(ForeignKey("marinas.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    berth_slot_id: Mapped[int] = mapped_column(ForeignKey("berth_slots.id"), nullable=False, index=True)
    boat_id: Mapped[int] = mapped_column(ForeignKey("boats.id"), nullable=False, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    extra_services_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending", index=True)
    approval_status: Mapped[str] = mapped_column(String(40), nullable=False, default="not_required", index=True)
    payment_status: Mapped[str] = mapped_column(String(40), nullable=False, default="unpaid", index=True)
    arrival_time: Mapped[str | None] = mapped_column(String(20), nullable=True)
    departure_time: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    marina = relationship("Marina", back_populates="bookings")
    user = relationship("User", back_populates="bookings")
    berth_slot = relationship("BerthSlot", back_populates="bookings")
    boat = relationship("Boat", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")
    extra_services = relationship("BookingExtraService", back_populates="booking")
