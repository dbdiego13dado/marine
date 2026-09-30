from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.bookings import BookingCreate, BookingRead
from app.services.booking_service import create_booking, list_bookings

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingRead])
def get_bookings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_bookings(db, current_user)


@router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def post_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_booking(db, payload, current_user)
