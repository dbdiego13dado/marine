from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Marina(Base):
    __tablename__ = "marinas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(80), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    structure_type: Mapped[str] = mapped_column(String(40), nullable=False, default="marina", index=True)
    timezone: Mapped[str] = mapped_column(String(80), nullable=False, default="Europe/Rome")
    default_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    public_slug: Mapped[str | None] = mapped_column(String(140), nullable=True, unique=True, index=True)
    short_description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    long_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    subscription_plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("subscription_plans.id"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    subscription_plan = relationship("SubscriptionPlan", back_populates="marinas")
    users = relationship("User", back_populates="marina")
    berth_slots = relationship("BerthSlot", back_populates="marina")
    boats = relationship("Boat", back_populates="marina")
    bookings = relationship("Booking", back_populates="marina")
    payments = relationship("Payment", back_populates="marina")
    maps = relationship("MarinaMap", back_populates="marina")
    subscriptions = relationship("MarinaSubscription", back_populates="marina")
    settings = relationship("MarinaSettings", back_populates="marina", uselist=False)
    services = relationship("MarinaService", back_populates="marina")
    zones = relationship("MarinaZone", back_populates="marina")
    photos = relationship("MarinaPhoto", back_populates="marina")
    extra_services = relationship("ExtraService", back_populates="marina")
    seasonal_rates = relationship("SeasonalRate", back_populates="marina")
    waitlist_requests = relationship("WaitlistRequest", back_populates="marina")
