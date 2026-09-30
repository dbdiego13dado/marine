from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ExtraService(Base):
    __tablename__ = "extra_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    marina_id: Mapped[int] = mapped_column(ForeignKey("marinas.id"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    billing_mode: Mapped[str] = mapped_column(String(40), nullable=False, default="per_booking")
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    customer_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    requires_staff_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    marina = relationship("Marina", back_populates="extra_services")
    bookings = relationship("BookingExtraService", back_populates="extra_service")


class BookingExtraService(Base):
    __tablename__ = "booking_extra_services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), nullable=False, index=True)
    extra_service_id: Mapped[int] = mapped_column(ForeignKey("extra_services.id"), nullable=False, index=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    booking = relationship("Booking", back_populates="extra_services")
    extra_service = relationship("ExtraService", back_populates="bookings")
