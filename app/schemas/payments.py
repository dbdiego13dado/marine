from datetime import datetime

from app.schemas.common import ORMModel


class PaymentCreate(ORMModel):
    booking_id: int
    provider: str = "mock"


class MockCheckoutRequest(ORMModel):
    booking_id: int


class PaymentUpdate(ORMModel):
    status: str | None = None
    provider_reference: str | None = None


class PaymentRead(ORMModel):
    id: int
    marina_id: int
    booking_id: int
    provider: str
    amount: float
    currency: str
    status: str
    provider_reference: str | None = None
    created_at: datetime
