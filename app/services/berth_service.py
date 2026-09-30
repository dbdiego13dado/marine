from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.berth import BerthSlot
from app.models.marina import Marina
from app.schemas.berths import BerthSlotCreate
from app.services import subscription_service


def list_berths(db: Session, marina_id: int | None = None) -> list[BerthSlot]:
    query = db.query(BerthSlot).filter(BerthSlot.active.is_(True))
    if marina_id is not None:
        query = query.filter(BerthSlot.marina_id == marina_id)
    return query.order_by(BerthSlot.code).all()


def get_berth(db: Session, berth_id: int) -> BerthSlot:
    berth = db.get(BerthSlot, berth_id)
    if berth is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Berth slot not found")
    return berth


def create_berth(db: Session, payload: BerthSlotCreate) -> BerthSlot:
    marina = db.get(Marina, payload.marina_id)
    if marina is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marina not found")
    subscription_service.ensure_berth_limit(db, marina)
    duplicate = (
        db.query(BerthSlot)
        .filter(BerthSlot.marina_id == payload.marina_id, BerthSlot.code == payload.code)
        .first()
    )
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Berth code already exists")
    berth = BerthSlot(**payload.model_dump())
    db.add(berth)
    db.commit()
    db.refresh(berth)
    return berth
