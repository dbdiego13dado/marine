from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WaitlistRequest(Base):
    __tablename__ = "waitlist_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    marina_id: Mapped[int] = mapped_column(ForeignKey("marinas.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    boat_id: Mapped[int | None] = mapped_column(ForeignKey("boats.id"), nullable=True, index=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("marina_zones.id"), nullable=True, index=True)
    boat_name: Mapped[str] = mapped_column(String(120), nullable=False)
    boat_type: Mapped[str] = mapped_column(String(40), nullable=False, default="other")
    length_m: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    beam_m: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    draft_m: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    desired_start_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    desired_end_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="open", index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    marina = relationship("Marina", back_populates="waitlist_requests")
    user = relationship("User")
    boat = relationship("Boat")
    zone = relationship("MarinaZone", back_populates="waitlist_requests")
