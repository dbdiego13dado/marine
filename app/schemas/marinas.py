from datetime import datetime

from pydantic import Field, field_validator

from app.schemas.common import ORMModel, SUPPORTED_CURRENCIES


class MarinaBase(ORMModel):
    name: str = Field(min_length=2, max_length=120)
    country: str = Field(min_length=2, max_length=80)
    city: str = Field(min_length=2, max_length=80)
    address: str = Field(min_length=2, max_length=255)
    timezone: str = "Europe/Rome"
    default_currency: str = "EUR"
    active: bool = True
    subscription_plan_id: int | None = None

    @field_validator("default_currency")
    @classmethod
    def validate_currency(cls, value: str) -> str:
        if value not in SUPPORTED_CURRENCIES:
            raise ValueError("Unsupported currency")
        return value


class MarinaCreate(MarinaBase):
    pass


class MarinaUpdate(ORMModel):
    name: str | None = None
    country: str | None = None
    city: str | None = None
    address: str | None = None
    timezone: str | None = None
    default_currency: str | None = None
    active: bool | None = None
    subscription_plan_id: int | None = None


class MarinaRead(MarinaBase):
    id: int
    created_at: datetime
