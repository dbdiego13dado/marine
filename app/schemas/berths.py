from pydantic import Field, field_validator

from app.schemas.common import BERTH_CATEGORIES, BERTH_STATUSES, BERTH_USAGE_TYPES, ORMModel


class BerthSlotBase(ORMModel):
    marina_id: int
    zone_id: int | None = None
    code: str = Field(min_length=1, max_length=40)
    max_length_m: float = Field(gt=0)
    max_beam_m: float = Field(gt=0)
    max_draft_m: float = Field(gt=0)
    category: str = "other"
    usage_type: str = "transient"
    price_per_day: float = Field(ge=0)
    price_per_week: float = Field(ge=0)
    price_per_month: float = Field(ge=0)
    status: str = "available"
    special_approval_required: bool = False
    notes: str | None = None
    active: bool = True

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        if value not in BERTH_CATEGORIES:
            raise ValueError("Unsupported berth category")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in BERTH_STATUSES:
            raise ValueError("Unsupported berth status")
        return value

    @field_validator("usage_type")
    @classmethod
    def validate_usage_type(cls, value: str) -> str:
        if value not in BERTH_USAGE_TYPES:
            raise ValueError("Unsupported berth usage type")
        return value


class BerthSlotCreate(BerthSlotBase):
    pass


class BerthSlotUpdate(ORMModel):
    zone_id: int | None = None
    code: str | None = None
    max_length_m: float | None = Field(default=None, gt=0)
    max_beam_m: float | None = Field(default=None, gt=0)
    max_draft_m: float | None = Field(default=None, gt=0)
    category: str | None = None
    usage_type: str | None = None
    price_per_day: float | None = Field(default=None, ge=0)
    price_per_week: float | None = Field(default=None, ge=0)
    price_per_month: float | None = Field(default=None, ge=0)
    status: str | None = None
    special_approval_required: bool | None = None
    notes: str | None = None
    active: bool | None = None


class BerthSlotRead(BerthSlotBase):
    id: int
