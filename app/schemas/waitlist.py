from datetime import date, datetime

from pydantic import Field, model_validator

from app.schemas.common import ORMModel


class WaitlistRequestBase(ORMModel):
    marina_id: int
    user_id: int
    boat_id: int | None = None
    zone_id: int | None = None
    boat_name: str = Field(min_length=1, max_length=120)
    boat_type: str = "other"
    length_m: float = Field(gt=0)
    beam_m: float = Field(gt=0)
    draft_m: float = Field(gt=0)
    desired_start_date: date
    desired_end_date: date
    status: str = "open"
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.desired_end_date <= self.desired_start_date:
            raise ValueError("desired_end_date must be after desired_start_date")
        return self


class WaitlistRequestCreate(WaitlistRequestBase):
    pass


class WaitlistRequestRead(WaitlistRequestBase):
    id: int
    created_at: datetime
