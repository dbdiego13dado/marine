from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    marina_id: Mapped[int | None] = mapped_column(ForeignKey("marinas.id"), nullable=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(40), nullable=False, default="customer", index=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    language_preference: Mapped[str] = mapped_column(String(5), nullable=False, default="en")
    currency_preference: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    marina = relationship("Marina", back_populates="users")
    boats = relationship("Boat", back_populates="user")
    bookings = relationship("Booking", back_populates="user")
