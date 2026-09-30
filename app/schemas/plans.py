from app.schemas.common import ORMModel


class SubscriptionPlanCreate(ORMModel):
    name: str
    price_monthly: float
    currency: str = "EUR"
    max_berths: int
    max_staff_users: int
    allow_map: bool = False
    allow_payments: bool = False
    allow_advanced_dashboard: bool = False
    active: bool = True


class SubscriptionPlanUpdate(ORMModel):
    price_monthly: float | None = None
    max_berths: int | None = None
    max_staff_users: int | None = None
    allow_map: bool | None = None
    allow_payments: bool | None = None
    allow_advanced_dashboard: bool | None = None
    active: bool | None = None


class SubscriptionPlanRead(SubscriptionPlanCreate):
    id: int
