from datetime import datetime

from pydantic import Field

from app.schemas.common import ORMModel


class BoatBase(ORMModel):
    user_id: int
    marina_id: int
    name: str = Field(min_length=1, max_length=120)
    boat_type: str = "other"
    length_m: float = Field(gt=0)
    beam_m: float = Field(gt=0)
    draft_m: float = Field(gt=0)
    engine_power_hp: int | None = None
    registration_code: str | None = None
    insurance_notes: str | None = None
    notes: str | None = None


class BoatCreate(BoatBase):
    pass


class BoatUpdate(ORMModel):
    name: str | None = None
    boat_type: str | None = None
    length_m: float | None = Field(default=None, gt=0)
    beam_m: float | None = Field(default=None, gt=0)
    draft_m: float | None = Field(default=None, gt=0)
    engine_power_hp: int | None = None
    registration_code: str | None = None
    insurance_notes: str | None = None
    notes: str | None = None


class BoatRead(BoatBase):
    id: int
    created_at: datetime
