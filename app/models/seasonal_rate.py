from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SeasonalRate(Base):
    __tablename__ = "seasonal_rates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    marina_id: Mapped[int] = mapped_column(ForeignKey("marinas.id"), nullable=False, index=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("marina_zones.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    berth_category: Mapped[str | None] = mapped_column(String(40), nullable=True)
    start_month: Mapped[int] = mapped_column(Integer, nullable=False)
    start_day: Mapped[int] = mapped_column(Integer, nullable=False)
    end_month: Mapped[int] = mapped_column(Integer, nullable=False)
    end_day: Mapped[int] = mapped_column(Integer, nullable=False)
    day_multiplier: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False, default=1)
    week_multiplier: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False, default=1)
    month_multiplier: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False, default=1)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    marina = relationship("Marina", back_populates="seasonal_rates")
    zone = relationship("MarinaZone", back_populates="seasonal_rates")
