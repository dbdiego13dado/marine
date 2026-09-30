from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import ensure_marina_access
from app.models.berth import BerthSlot
from app.models.boat import Boat
from app.models.booking import Booking
from app.models.extra_service import BookingExtraService, ExtraService
from app.models.marina import Marina
from app.models.user import User
from app.models.waitlist import WaitlistRequest
from app.schemas.bookings import BookingCreate
from app.schemas.waitlist import WaitlistRequestCreate
from app.services.pricing_service import calculate_booking_price, calculate_extra_service_total
from app.services.subscription_service import ensure_subscription_active


def _has_overlap(db: Session, payload: BookingCreate) -> bool:
    return (
        db.query(Booking)
        .filter(
            Booking.berth_slot_id == payload.berth_slot_id,
            Booking.status.in_(["pending", "confirmed"]),
            Booking.start_date < payload.end_date,
            Booking.end_date > payload.start_date,
        )
        .first()
        is not None
    )


def _berth_has_overlap(db: Session, berth_id: int, payload: BookingCreate) -> bool:
    return (
        db.query(Booking)
        .filter(
            Booking.berth_slot_id == berth_id,
            Booking.status.in_(["pending", "confirmed"]),
            Booking.start_date < payload.end_date,
            Booking.end_date > payload.start_date,
        )
        .first()
        is not None
    )


def _capacity_tuple(berth: BerthSlot) -> tuple[Decimal, Decimal, Decimal]:
    return (
        Decimal(str(berth.max_length_m)),
        Decimal(str(berth.max_beam_m)),
        Decimal(str(berth.max_draft_m)),
    )


def find_matching_transient_berths(
    db: Session,
    marina_id: int,
    boat_type: str,
    length_m: float,
    beam_m: float,
    draft_m: float,
    start_date=None,
    end_date=None,
) -> list[BerthSlot]:
    query = (
        db.query(BerthSlot)
        .filter(
            BerthSlot.marina_id == marina_id,
            BerthSlot.active.is_(True),
            BerthSlot.status == "available",
            BerthSlot.usage_type == "transient",
            BerthSlot.category == boat_type,
            BerthSlot.max_length_m >= length_m,
            BerthSlot.max_beam_m >= beam_m,
            BerthSlot.max_draft_m >= draft_m,
        )
        .order_by(BerthSlot.max_length_m, BerthSlot.max_beam_m, BerthSlot.max_draft_m, BerthSlot.code)
    )
    berths = query.all()
    if start_date is None or end_date is None:
        return berths
    probe = BookingCreate(
        marina_id=marina_id,
        user_id=0,
        berth_slot_id=berths[0].id if berths else 0,
        boat_id=0,
        start_date=start_date,
        end_date=end_date,
    )
    return [berth for berth in berths if not _berth_has_overlap(db, berth.id, probe)]


def _is_best_fit_berth(db: Session, payload: BookingCreate, boat: Boat, selected_berth: BerthSlot) -> bool:
    available_fitting_berths = find_matching_transient_berths(
        db,
        payload.marina_id,
        boat.boat_type,
        float(boat.length_m),
        float(boat.beam_m),
        float(boat.draft_m),
        payload.start_date,
        payload.end_date,
    )
    if not available_fitting_berths:
        return False
    best_capacity = min(_capacity_tuple(berth) for berth in available_fitting_berths)
    return _capacity_tuple(selected_berth) == best_capacity


def _normalize_extra_service_requests(extra_service_requests: list[dict] | None) -> list[dict]:
    normalized = []
    for item in extra_service_requests or []:
        service_id = int(item.get("service_id") or 0)
        quantity = max(1, int(item.get("quantity") or 1))
        if service_id:
            normalized.append({"service_id": service_id, "quantity": quantity})
    return normalized


def _resolve_extra_services(
    db: Session,
    marina: Marina,
    extra_service_requests: list[dict] | None,
    booking_days: int,
) -> tuple[list[dict], Decimal, bool]:
    selected_services: list[dict] = []
    total = Decimal("0.00")
    needs_approval = False
    for item in _normalize_extra_service_requests(extra_service_requests):
        service = db.get(ExtraService, item["service_id"])
        if service is None or service.marina_id != marina.id or not service.active or not service.customer_visible:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servizio extra non trovato")
        line_total = calculate_extra_service_total(service, item["quantity"], booking_days)
        total += line_total
        if service.requires_staff_approval:
            needs_approval = True
        selected_services.append(
            {
                "service": service,
                "quantity": item["quantity"],
                "unit_price": Decimal(str(service.amount)),
                "total_price": line_total,
            }
        )
    return selected_services, total.quantize(Decimal("0.01")), needs_approval


def create_booking(
    db: Session,
    payload: BookingCreate,
    current_user: User,
    extra_service_requests: list[dict] | None = None,
) -> Booking:
    booking_user = db.get(User, payload.user_id)
    marina = db.get(Marina, payload.marina_id)
    berth = db.get(BerthSlot, payload.berth_slot_id)
    boat = db.get(Boat, payload.boat_id)

    if not all([booking_user, marina, berth, boat]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking related record not found")

    if current_user.role == "customer" and current_user.id != payload.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customers can book only for themselves")
    ensure_marina_access(current_user, payload.marina_id)
    ensure_subscription_active(db, marina)

    if not booking_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    if not marina.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Marina is inactive")
    if not berth.active or berth.status != "available":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Berth is not available")
    if berth.usage_type != "transient":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Questo posto non e prenotabile dai clienti occasionali.")
    if berth.marina_id != marina.id or boat.marina_id != marina.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Boat and berth must belong to marina")
    if boat.user_id != booking_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Boat must belong to the booking user")
    if berth.category != boat.boat_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Il posto selezionato non corrisponde alla tipologia dell'imbarcazione.")
    if (
        Decimal(str(boat.length_m)) > Decimal(str(berth.max_length_m))
        or Decimal(str(boat.beam_m)) > Decimal(str(berth.max_beam_m))
        or Decimal(str(boat.draft_m)) > Decimal(str(berth.max_draft_m))
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le dimensioni della barca superano i limiti del posto selezionato.")
    if _has_overlap(db, payload):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Il posto selezionato e gia occupato nelle date richieste.")
    if not _is_best_fit_berth(db, payload, boat, berth):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Il posto selezionato e troppo grande per questa barca: scegli uno dei posti evidenziati come piu adatti.",
        )

    booking_days = (payload.end_date - payload.start_date).days
    selected_services, extras_total, extras_need_approval = _resolve_extra_services(
        db,
        marina,
        extra_service_requests,
        booking_days,
    )
    berth_needs_approval = berth.special_approval_required
    approval_status = "pending_staff" if berth_needs_approval or extras_need_approval else "not_required"

    total_price = payload.total_price
    if total_price is None:
        berth_total = calculate_booking_price(berth, payload.start_date, payload.end_date, db=db)
        total_price = float((berth_total + extras_total).quantize(Decimal("0.01")))

    booking = Booking(
        marina_id=payload.marina_id,
        user_id=payload.user_id,
        berth_slot_id=payload.berth_slot_id,
        boat_id=payload.boat_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        total_price=total_price,
        extra_services_total=float(extras_total),
        currency=payload.currency or marina.default_currency,
        status=payload.status,
        approval_status=approval_status,
        payment_status=payload.payment_status,
        arrival_time=payload.arrival_time,
        departure_time=payload.departure_time,
        notes=payload.notes,
    )
    db.add(booking)
    db.flush()
    for service_line in selected_services:
        db.add(
            BookingExtraService(
                booking_id=booking.id,
                extra_service_id=service_line["service"].id,
                quantity=service_line["quantity"],
                unit_price=service_line["unit_price"],
                total_price=service_line["total_price"],
            )
        )
    db.commit()
    db.refresh(booking)
    return booking


def list_bookings(db: Session, current_user: User) -> list[Booking]:
    query = db.query(Booking)
    if current_user.role == "customer":
        query = query.filter(Booking.user_id == current_user.id)
    elif current_user.role in {"marina_admin", "staff"}:
        query = query.filter(Booking.marina_id == current_user.marina_id)
    return query.order_by(Booking.start_date.desc()).all()


def create_waitlist_request(db: Session, payload: WaitlistRequestCreate, current_user: User) -> WaitlistRequest:
    marina = db.get(Marina, payload.marina_id)
    if marina is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marina not found")
    if current_user.role == "customer" and current_user.id != payload.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Customers can submit only own waitlist requests")
    ensure_marina_access(current_user, payload.marina_id)
    waitlist_request = WaitlistRequest(**payload.model_dump())
    db.add(waitlist_request)
    db.commit()
    db.refresh(waitlist_request)
    return waitlist_request


def list_waitlist_requests(db: Session, current_user: User) -> list[WaitlistRequest]:
    query = db.query(WaitlistRequest)
    if current_user.role == "customer":
        query = query.filter(WaitlistRequest.user_id == current_user.id)
    elif current_user.role in {"marina_admin", "staff"}:
        query = query.filter(WaitlistRequest.marina_id == current_user.marina_id)
    return query.order_by(WaitlistRequest.created_at.desc()).all()
