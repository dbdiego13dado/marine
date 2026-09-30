from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import ensure_marina_access, get_current_user
from app.database import get_db
from app.models.boat import Boat
from app.models.user import User
from app.schemas.boats import BoatCreate, BoatRead

router = APIRouter(prefix="/boats", tags=["boats"])


@router.get("", response_model=list[BoatRead])
def list_boats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Boat)
    if current_user.role == "customer":
        query = query.filter(Boat.user_id == current_user.id)
    elif current_user.role in {"marina_admin", "staff"}:
        query = query.filter(Boat.marina_id == current_user.marina_id)
    return query.order_by(Boat.created_at.desc()).all()


@router.post("", response_model=BoatRead, status_code=status.HTTP_201_CREATED)
def create_boat(
    payload: BoatCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "customer" and payload.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customers can create only own boats")
    ensure_marina_access(current_user, payload.marina_id)
    boat = Boat(**payload.model_dump())
    db.add(boat)
    db.commit()
    db.refresh(boat)
    return boat
