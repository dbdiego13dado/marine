import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import ensure_marina_access
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.user import User
from app.services.subscription_service import ensure_feature_allowed


def list_payments(db: Session, current_user: User) -> list[Payment]:
    query = db.query(Payment)
    if current_user.role == "customer":
        query = query.join(Booking).filter(Booking.user_id == current_user.id)
    elif current_user.role in {"marina_admin", "staff"}:
        query = query.filter(Payment.marina_id == current_user.marina_id)
    return query.order_by(Payment.created_at.desc()).all()


def mock_checkout(
    db: Session,
    booking_id: int,
    current_user: User,
    provider: str = "mock",
    payment_reference: str | None = None,
) -> Payment:
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if current_user.role == "customer" and booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customers can pay only own bookings")
    ensure_marina_access(current_user, booking.marina_id)
    ensure_feature_allowed(db, booking.marina, "payments")
    if booking.payment_status == "paid":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking is already paid")

    payment = Payment(
        marina_id=booking.marina_id,
        booking_id=booking.id,
        provider=provider,
        amount=booking.total_price,
        currency=booking.currency,
        status="paid",
        provider_reference=payment_reference or f"{provider}_{secrets.token_hex(8)}",
    )
    booking.payment_status = "paid"
    if booking.status == "pending" and booking.approval_status in {"not_required", "approved"}:
        booking.status = "confirmed"
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
