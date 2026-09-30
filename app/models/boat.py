from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Boat(Base):
    __tablename__ = "boats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    marina_id: Mapped[int] = mapped_column(ForeignKey("marinas.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    boat_type: Mapped[str] = mapped_column(String(40), nullable=False, default="other")
    length_m: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    beam_m: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    draft_m: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    engine_power_hp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    registration_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    insurance_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="boats")
    marina = relationship("Marina", back_populates="boats")
    bookings = relationship("Booking", back_populates="boat")
