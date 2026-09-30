from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MarinaZone(Base):
    __tablename__ = "marina_zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    marina_id: Mapped[int] = mapped_column(ForeignKey("marinas.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    zone_type: Mapped[str] = mapped_column(String(40), nullable=False, default="general")
    color: Mapped[str] = mapped_column(String(20), nullable=False, default="#007c74")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    customer_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    marina = relationship("Marina", back_populates="zones")
    berths = relationship("BerthSlot", back_populates="zone")
    seasonal_rates = relationship("SeasonalRate", back_populates="zone")
    waitlist_requests = relationship("WaitlistRequest", back_populates="zone")
