from datetime import date, datetime

from pydantic import Field, field_validator, model_validator

from app.schemas.common import APPROVAL_STATUSES, BOOKING_STATUSES, ORMModel, PAYMENT_STATUSES


class BookingBase(ORMModel):
    marina_id: int
    user_id: int
    berth_slot_id: int
    boat_id: int
    start_date: date
    end_date: date
    total_price: float | None = None
    extra_services_total: float | None = 0
    currency: str = "EUR"
    status: str = "pending"
    approval_status: str = "not_required"
    payment_status: str = "unpaid"
    arrival_time: str | None = None
    departure_time: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in BOOKING_STATUSES:
            raise ValueError("Unsupported booking status")
        return value

    @field_validator("payment_status")
    @classmethod
    def validate_payment_status(cls, value: str) -> str:
        if value not in PAYMENT_STATUSES:
            raise ValueError("Unsupported payment status")
        return value

    @field_validator("approval_status")
    @classmethod
    def validate_approval_status(cls, value: str) -> str:
        if value not in APPROVAL_STATUSES:
            raise ValueError("Unsupported approval status")
        return value


class BookingCreate(BookingBase):
    total_price: float | None = Field(default=None, ge=0)


class BookingUpdate(ORMModel):
    status: str | None = None
    approval_status: str | None = None
    payment_status: str | None = None
    notes: str | None = None


class BookingRead(BookingBase):
    id: int
    total_price: float
    created_at: datetime
