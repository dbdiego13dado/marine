from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.berth import BerthSlot
from app.models.booking import Booking
from app.models.marina import Marina
from app.models.payment import Payment
from app.services.subscription_service import ensure_subscription_active


def get_dashboard_summary(db: Session, marina: Marina) -> dict:
    ensure_subscription_active(db, marina)
    total_berths = db.query(BerthSlot).filter(BerthSlot.marina_id == marina.id, BerthSlot.active.is_(True)).count()
    today = date.today()
    occupied_berth_ids = {
        berth_id
        for (berth_id,) in (
            db.query(Booking.berth_slot_id)
            .filter(
                Booking.marina_id == marina.id,
                Booking.status.in_(["confirmed", "pending"]),
                Booking.start_date <= today,
                Booking.end_date > today,
            )
            .all()
        )
    }
    reserved_owner_berths = (
        db.query(BerthSlot)
        .filter(BerthSlot.marina_id == marina.id, BerthSlot.active.is_(True), BerthSlot.usage_type == "owner")
        .count()
    )
    available_berths = (
        db.query(BerthSlot)
        .filter(
            BerthSlot.marina_id == marina.id,
            BerthSlot.active.is_(True),
            BerthSlot.status == "available",
            BerthSlot.usage_type == "transient",
            ~BerthSlot.id.in_(occupied_berth_ids or [0]),
        )
        .count()
    )
    occupied_berths = reserved_owner_berths + len(occupied_berth_ids)
    maintenance_berths = (
        db.query(BerthSlot)
        .filter(BerthSlot.marina_id == marina.id, BerthSlot.active.is_(True), BerthSlot.status == "maintenance")
        .count()
    )
    pending_bookings = db.query(Booking).filter(Booking.marina_id == marina.id, Booking.status == "pending").count()
    confirmed_bookings = db.query(Booking).filter(Booking.marina_id == marina.id, Booking.status == "confirmed").count()
    unpaid_bookings = db.query(Booking).filter(Booking.marina_id == marina.id, Booking.payment_status == "unpaid").count()
    month_start = today.replace(day=1)
    revenue = (
        db.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(
            Payment.marina_id == marina.id,
            Payment.status == "paid",
            func.date(Payment.created_at) >= month_start.isoformat(),
        )
        .scalar()
    )
    return {
        "total_berths": total_berths,
        "available_berths": available_berths,
        "occupied_berths": occupied_berths,
        "maintenance_berths": maintenance_berths,
        "pending_bookings": pending_bookings,
        "confirmed_bookings": confirmed_bookings,
        "unpaid_bookings": unpaid_bookings,
        "monthly_revenue_mock": float(revenue or 0),
        "currency": marina.default_currency,
    }
