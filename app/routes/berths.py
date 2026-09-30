from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import ensure_marina_access, get_current_user, require_roles
from app.database import get_db
from app.models.user import User
from app.schemas.berths import BerthSlotCreate, BerthSlotRead
from app.services import berth_service

router = APIRouter(prefix="/berths", tags=["berths"])


@router.get("", response_model=list[BerthSlotRead])
def list_berths(
    marina_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scoped_marina_id = marina_id
    if current_user.role != "super_admin":
        scoped_marina_id = current_user.marina_id
    return berth_service.list_berths(db, scoped_marina_id)


@router.post("", response_model=BerthSlotRead, status_code=status.HTTP_201_CREATED)
def create_berth(
    payload: BerthSlotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "marina_admin", "staff")),
):
    ensure_marina_access(current_user, payload.marina_id)
    return berth_service.create_berth(db, payload)
