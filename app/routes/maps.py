from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import ensure_marina_access, get_current_user
from app.database import get_db
from app.models.marina_map import MarinaMap
from app.models.user import User
from app.schemas.maps import MarinaMapRead
from app.services.subscription_service import ensure_feature_allowed

router = APIRouter(prefix="/maps", tags=["maps"])


@router.get("", response_model=list[MarinaMapRead])
def list_maps(
    marina_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scoped_marina_id = marina_id if current_user.role == "super_admin" else current_user.marina_id
    query = db.query(MarinaMap).options(joinedload(MarinaMap.berth_positions))
    if scoped_marina_id is not None:
        query = query.filter(MarinaMap.marina_id == scoped_marina_id)
    maps = query.order_by(MarinaMap.name).all()
    for marina_map in maps:
        ensure_marina_access(current_user, marina_map.marina_id)
        ensure_feature_allowed(db, marina_map.marina, "map")
    return maps


@router.get("/{map_id}", response_model=MarinaMapRead)
def get_map(
    map_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    marina_map = (
        db.query(MarinaMap)
        .options(joinedload(MarinaMap.berth_positions))
        .filter(MarinaMap.id == map_id)
        .first()
    )
    if marina_map is None:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")
    ensure_marina_access(current_user, marina_map.marina_id)
    ensure_feature_allowed(db, marina_map.marina, "map")
    return marina_map
