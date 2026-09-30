from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.payments import MockCheckoutRequest, PaymentRead
from app.services.payment_service import list_payments, mock_checkout

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("", response_model=list[PaymentRead])
def get_payments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_payments(db, current_user)


@router.post("/mock-checkout", response_model=PaymentRead)
def post_mock_checkout(
    payload: MockCheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return mock_checkout(db, payload.booking_id, current_user)
