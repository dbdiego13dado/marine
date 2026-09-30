from pydantic import Field

from app.schemas.berths import BerthSlotRead
from app.schemas.common import ORMModel


class BerthPositionCreate(ORMModel):
    marina_map_id: int
    berth_slot_id: int
    x: int
    y: int
    w: int
    h: int


class BerthPositionUpdate(ORMModel):
    x: int | None = None
    y: int | None = None
    w: int | None = None
    h: int | None = None


class BerthPositionRead(BerthPositionCreate):
    id: int
    berth_slot: BerthSlotRead | None = None


class MarinaMapCreate(ORMModel):
    marina_id: int
    name: str
    image_url: str
    width: int
    height: int


class MarinaMapUpdate(ORMModel):
    name: str | None = None
    image_url: str | None = None
    width: int | None = None
    height: int | None = None


class MarinaMapRead(MarinaMapCreate):
    id: int
    berth_positions: list[BerthPositionRead] = Field(default_factory=list)
