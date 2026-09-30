from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_db
from app.models.marina import Marina
from app.models.subscription import SubscriptionPlan
from app.models.user import User
from app.schemas.marinas import MarinaCreate, MarinaRead
from app.services.subscription_service import create_or_update_subscription

router = APIRouter(prefix="/marinas", tags=["marinas"])


@router.get("", response_model=list[MarinaRead])
def list_marinas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Marina)
    if current_user.role != "super_admin":
        query = query.filter(Marina.id == current_user.marina_id)
    return query.order_by(Marina.name).all()


@router.post("", response_model=MarinaRead, status_code=status.HTTP_201_CREATED)
def create_marina(
    payload: MarinaCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("super_admin")),
):
    plan_id = payload.subscription_plan_id
    if plan_id is None:
        free_plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == "free").first()
        plan_id = free_plan.id if free_plan else None
    marina = Marina(**payload.model_dump(exclude={"subscription_plan_id"}), subscription_plan_id=plan_id)
    db.add(marina)
    db.flush()
    if plan_id:
        plan = db.get(SubscriptionPlan, plan_id)
        if plan:
            create_or_update_subscription(db, marina, plan)
    db.commit()
    db.refresh(marina)
    return marina
