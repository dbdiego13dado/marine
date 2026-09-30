from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.subscription import SubscriptionPlan
from app.schemas.plans import SubscriptionPlanRead

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[SubscriptionPlanRead])
def list_plans(db: Session = Depends(get_db)):
    return db.query(SubscriptionPlan).filter(SubscriptionPlan.active.is_(True)).order_by(SubscriptionPlan.price_monthly).all()
