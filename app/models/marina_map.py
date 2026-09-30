from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MarinaMap(Base):
    __tablename__ = "marina_maps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    marina_id: Mapped[int] = mapped_column(ForeignKey("marinas.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)

    marina = relationship("Marina", back_populates="maps")
    berth_positions = relationship("BerthPosition", back_populates="marina_map")


class BerthPosition(Base):
    __tablename__ = "berth_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    marina_map_id: Mapped[int] = mapped_column(ForeignKey("marina_maps.id"), nullable=False, index=True)
    berth_slot_id: Mapped[int] = mapped_column(ForeignKey("berth_slots.id"), nullable=False, index=True)
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    w: Mapped[int] = mapped_column(Integer, nullable=False)
    h: Mapped[int] = mapped_column(Integer, nullable=False)

    marina_map = relationship("MarinaMap", back_populates="berth_positions")
    berth_slot = relationship("BerthSlot", back_populates="positions")
