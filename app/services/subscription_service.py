from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.berth import BerthSlot
from app.models.marina import Marina
from app.models.subscription import MarinaSubscription, SubscriptionPlan
from app.models.user import User


def get_plan_by_name(db: Session, name: str) -> SubscriptionPlan | None:
    return db.query(SubscriptionPlan).filter(SubscriptionPlan.name == name).first()


def get_current_plan(db: Session, marina: Marina) -> SubscriptionPlan:
    plan = marina.subscription_plan
    if plan and plan.active:
        return plan
    subscription = (
        db.query(MarinaSubscription)
        .filter(
            MarinaSubscription.marina_id == marina.id,
            MarinaSubscription.status == "active",
        )
        .order_by(MarinaSubscription.start_date.desc())
        .first()
    )
    if subscription and subscription.subscription_plan.active:
        return subscription.subscription_plan
    raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="No active SaaS plan")


def ensure_subscription_active(db: Session, marina: Marina) -> SubscriptionPlan:
    if not marina.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Marina is not active")
    return get_current_plan(db, marina)


def ensure_feature_allowed(db: Session, marina: Marina, feature: str) -> SubscriptionPlan:
    plan = ensure_subscription_active(db, marina)
    feature_flags = {
        "map": plan.allow_map,
        "payments": plan.allow_payments,
        "advanced_dashboard": plan.allow_advanced_dashboard,
    }
    if feature not in feature_flags:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown SaaS feature")
    if not feature_flags[feature]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Feature '{feature}' is not available on the current plan",
        )
    return plan


def ensure_berth_limit(db: Session, marina: Marina) -> None:
    plan = ensure_subscription_active(db, marina)
    count = (
        db.query(BerthSlot)
        .filter(BerthSlot.marina_id == marina.id, BerthSlot.active.is_(True))
        .count()
    )
    if count >= plan.max_berths:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Current SaaS plan berth limit reached",
        )


def ensure_staff_limit(db: Session, marina: Marina) -> None:
    plan = ensure_subscription_active(db, marina)
    if plan.max_staff_users < 0:
        return
    count = (
        db.query(User)
        .filter(
            User.marina_id == marina.id,
            User.role.in_(["marina_admin", "staff"]),
            User.is_active.is_(True),
        )
        .count()
    )
    if count >= plan.max_staff_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Current SaaS plan staff user limit reached",
        )


def create_or_update_subscription(
    db: Session,
    marina: Marina,
    plan: SubscriptionPlan,
    subscription_status: str = "active",
) -> MarinaSubscription:
    marina.subscription_plan_id = plan.id
    subscription = (
        db.query(MarinaSubscription)
        .filter(MarinaSubscription.marina_id == marina.id, MarinaSubscription.status == "active")
        .first()
    )
    if subscription is None:
        subscription = MarinaSubscription(
            marina_id=marina.id,
            subscription_plan_id=plan.id,
            status=subscription_status,
            start_date=date.today(),
        )
        db.add(subscription)
    else:
        subscription.subscription_plan_id = plan.id
        subscription.status = subscription_status
        subscription.end_date = None
    db.flush()
    return subscription
