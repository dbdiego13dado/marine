from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import ensure_marina_access
from app.database import get_db
from app.i18n import translator
from app.models.berth import BerthSlot
from app.models.boat import Boat
from app.models.booking import Booking
from app.models.extra_service import BookingExtraService, ExtraService
from app.models.marina import Marina
from app.models.marina_map import BerthPosition, MarinaMap
from app.models.marina_photo import MarinaPhoto
from app.models.marina_service import MarinaService
from app.models.marina_settings import MarinaSettings
from app.models.marina_zone import MarinaZone
from app.models.seasonal_rate import SeasonalRate
from app.models.user import User
from app.models.waitlist import WaitlistRequest
from app.schemas.berths import BerthSlotCreate
from app.schemas.boats import BoatCreate
from app.schemas.bookings import BookingCreate
from app.schemas.waitlist import WaitlistRequestCreate
from app.services import berth_service, booking_service, dashboard_service, marina_profile_service, payment_service

router = APIRouter(tags=["ui"])
templates = Jinja2Templates(directory="app/templates")
UPLOADS_DIR = Path(__file__).resolve().parent.parent / "uploads"


def _current_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = db.get(User, int(user_id))
    if user is None or not user.is_active:
        request.session.clear()
        return None
    return user


def _ctx(request: Request, user: User | None, **extra):
    language = request.session.get("language") or (user.language_preference if user else request.query_params.get("lang", "it"))
    if language not in {"it", "en"}:
        language = "it"
    return {"request": request, "current_user": user, "selected_language": language, "t": translator(language), **extra}


def _require_user(request: Request, db: Session) -> User | RedirectResponse:
    user = _current_user(request, db)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    return user


def _main_marina(db: Session, user: User) -> Marina | None:
    if user.role == "super_admin":
        return db.query(Marina).filter(Marina.active.is_(True)).order_by(Marina.id).first()
    return db.get(Marina, user.marina_id)


def _form_float(value: object) -> float:
    return float(str(value or "").strip().replace(",", "."))


def _form_int(value: object, default: int = 0) -> int:
    raw = str(value or "").strip()
    return int(raw) if raw else default


def _require_admin_user(request: Request, db: Session) -> User | RedirectResponse:
    user = _require_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    if user.role == "customer":
        raise HTTPException(status_code=403, detail="Area riservata ad amministratore e staff")
    return user


def _get_or_create_settings(db: Session, marina: Marina) -> MarinaSettings:
    return marina_profile_service.get_or_create_settings(db, marina)


def _admin_redirect(flag: str = "saved") -> RedirectResponse:
    return RedirectResponse(f"/admin?{flag}=1", status_code=303)


def _map_redirect(flag: str = "saved") -> RedirectResponse:
    return RedirectResponse(f"/map?{flag}=1", status_code=303)


@router.post("/ui/language")
async def set_language(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    language = str(form.get("language") or "it")
    if language not in {"it", "en"}:
        language = "it"
    request.session["language"] = language
    user = _current_user(request, db)
    if user is not None:
        user.language_preference = language
        db.commit()
    return RedirectResponse(str(form.get("next") or request.headers.get("referer") or "/"), status_code=303)


def _get_accessible_booking(db: Session, booking_id: int, user: User) -> Booking:
    booking = (
        db.query(Booking)
        .options(
            joinedload(Booking.boat),
            joinedload(Booking.berth_slot),
            joinedload(Booking.user),
            joinedload(Booking.marina),
            joinedload(Booking.extra_services).joinedload(BookingExtraService.extra_service),
        )
        .filter(Booking.id == booking_id)
        .first()
    )
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if user.role == "customer" and booking.user_id != user.id:
        raise HTTPException(status_code=403, detail="Customers can access only own bookings")
    ensure_marina_access(user, booking.marina_id)
    return booking


@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    if user.role == "customer":
        return RedirectResponse("/ui/bookings", status_code=303)
    return RedirectResponse("/dashboard", status_code=303)


@router.get("/login")
def login_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "login.html", _ctx(request, _current_user(request, db)))


@router.get("/register")
def register_page(request: Request, db: Session = Depends(get_db)):
    marinas = db.query(Marina).filter(Marina.active.is_(True)).order_by(Marina.name).all()
    return templates.TemplateResponse(request, "register.html", _ctx(request, _current_user(request, db), marinas=marinas))


@router.get("/discover")
def discover_page(request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    marinas = marina_profile_service.list_public_marinas(db)
    return templates.TemplateResponse(request, "discover.html", _ctx(request, user, marinas=marinas))


@router.get("/marinas/{marina_id}/profile")
def public_marina_profile_page(marina_id: int, request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    marina = marina_profile_service.get_public_profile(db, marina_id)
    if marina is None:
        raise HTTPException(status_code=404, detail="Marina not found")
    settings = _get_or_create_settings(db, marina)
    services = marina_profile_service.list_visible_services(db, marina.id)
    photos = marina_profile_service.list_visible_photos(db, marina.id)
    zones = marina_profile_service.list_visible_zones(db, marina.id)
    seasonal_rates = marina_profile_service.list_seasonal_rates(db, marina.id)
    marina_map = (
        db.query(MarinaMap)
        .options(joinedload(MarinaMap.berth_positions).joinedload(BerthPosition.berth_slot))
        .filter(MarinaMap.marina_id == marina.id)
        .first()
    )
    return templates.TemplateResponse(
        request,
        "public_profile.html",
        _ctx(
            request,
            user,
            marina=marina,
            settings=settings,
            services=services,
            photos=photos,
            zones=zones,
            seasonal_rates=seasonal_rates,
            marina_map=marina_map,
        ),
    )


@router.get("/dashboard")
def marina_dashboard(request: Request, db: Session = Depends(get_db)):
    user = _require_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    if user.role == "customer":
        return RedirectResponse("/customer", status_code=303)
    marina = _main_marina(db, user)
    summary = dashboard_service.get_dashboard_summary(db, marina) if marina else None
    return templates.TemplateResponse(request, "dashboard.html", _ctx(request, user, marina=marina, summary=summary))


@router.get("/admin")
def admin_home(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    settings = _get_or_create_settings(db, marina)
    marina_map = (
        db.query(MarinaMap)
        .options(joinedload(MarinaMap.berth_positions).joinedload(BerthPosition.berth_slot))
        .filter(MarinaMap.marina_id == marina.id)
        .first()
    )
    positions = marina_map.berth_positions if marina_map else []
    berths = berth_service.list_berths(db, marina.id)
    services = db.query(MarinaService).filter(MarinaService.marina_id == marina.id).order_by(MarinaService.category, MarinaService.name).all()
    zones = db.query(MarinaZone).filter(MarinaZone.marina_id == marina.id).order_by(MarinaZone.sort_order, MarinaZone.name).all()
    photos = db.query(MarinaPhoto).filter(MarinaPhoto.marina_id == marina.id).order_by(MarinaPhoto.sort_order, MarinaPhoto.id).all()
    extra_services = db.query(ExtraService).filter(ExtraService.marina_id == marina.id).order_by(ExtraService.name).all()
    seasonal_rates = db.query(SeasonalRate).filter(SeasonalRate.marina_id == marina.id).order_by(SeasonalRate.start_month, SeasonalRate.start_day).all()
    waitlist_requests = db.query(WaitlistRequest).filter(WaitlistRequest.marina_id == marina.id).order_by(WaitlistRequest.created_at.desc()).limit(10).all()
    return templates.TemplateResponse(
        request,
        "admin.html",
        _ctx(
            request,
            user,
            marina=marina,
            settings=settings,
            marina_map=marina_map,
            positions=positions,
            berths=berths,
            services=services,
            zones=zones,
            photos=photos,
            extra_services=extra_services,
            seasonal_rates=seasonal_rates,
            waitlist_requests=waitlist_requests,
            saved=request.query_params.get("saved") == "1",
            error=request.query_params.get("error"),
        ),
    )


@router.post("/admin/marina")
async def update_admin_marina(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    form = await request.form()
    try:
        marina.name = str(form.get("name") or "").strip()
        marina.country = str(form.get("country") or "").strip()
        marina.city = str(form.get("city") or "").strip()
        marina.address = str(form.get("address") or "").strip()
        marina.structure_type = str(form.get("structure_type") or "marina").strip()
        marina.timezone = str(form.get("timezone") or "Europe/Rome").strip()
        marina.default_currency = str(form.get("default_currency") or "EUR").strip()
        marina.public_slug = str(form.get("public_slug") or "").strip() or None
        marina.short_description = str(form.get("short_description") or "").strip() or None
        marina.long_description = str(form.get("long_description") or "").strip() or None
        marina.latitude = _form_float(form.get("latitude")) if str(form.get("latitude") or "").strip() else None
        marina.longitude = _form_float(form.get("longitude")) if str(form.get("longitude") or "").strip() else None
        marina.active = form.get("active") == "1"
        db.commit()
        return _admin_redirect()
    except Exception as exc:
        db.rollback()
        return RedirectResponse(f"/admin?error={str(exc)}", status_code=303)


@router.post("/admin/settings")
async def update_admin_settings(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    settings = _get_or_create_settings(db, marina)
    form = await request.form()
    for field in [
        "office_email",
        "office_phone",
        "emergency_phone",
        "vhf_channel",
        "opening_hours",
        "check_in_start",
        "check_in_end",
        "check_out_time",
        "booking_terms",
        "map_notes",
        "nautical_access_notes",
        "seabed_notes",
    ]:
        setattr(settings, field, str(form.get(field) or "").strip())
    settings.accepts_catamarans = form.get("accepts_catamarans") == "1"
    settings.accepts_multihulls = form.get("accepts_multihulls") == "1"
    db.commit()
    return _admin_redirect()


@router.post("/admin/rules-pdf")
async def upload_admin_rules_pdf(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    settings = _get_or_create_settings(db, marina)
    form = await request.form()
    upload = form.get("rules_pdf")
    filename = getattr(upload, "filename", "")
    if not upload or not filename:
        return RedirectResponse("/admin?error=Seleziona un file PDF prima di salvare.", status_code=303)
    if not filename.lower().endswith(".pdf"):
        return RedirectResponse("/admin?error=Il regolamento deve essere un file PDF.", status_code=303)
    content = await upload.read()
    if not content.startswith(b"%PDF"):
        return RedirectResponse("/admin?error=Il file caricato non sembra un PDF valido.", status_code=303)
    rules_dir = UPLOADS_DIR / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    target = rules_dir / f"marina_{marina.id}_regolamento.pdf"
    target.write_bytes(content)
    settings.rules_pdf_url = f"/uploads/rules/{target.name}"
    db.commit()
    return _admin_redirect()


@router.post("/admin/map")
async def update_admin_map(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    form = await request.form()
    marina_map = db.query(MarinaMap).filter(MarinaMap.marina_id == marina.id).first()
    if marina_map is None:
        marina_map = MarinaMap(marina_id=marina.id, name="Main marina map", image_url="/static/marina-map-demo.svg", width=1000, height=620)
        db.add(marina_map)
    marina_map.name = str(form.get("name") or "").strip()
    marina_map.image_url = str(form.get("image_url") or "/static/marina-map-demo.svg").strip()
    marina_map.width = int(form.get("width") or 1000)
    marina_map.height = int(form.get("height") or 620)
    db.commit()
    return _admin_redirect()


@router.post("/admin/map/position")
async def upsert_admin_map_position(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    form = await request.form()
    marina_map = db.query(MarinaMap).filter(MarinaMap.marina_id == marina.id).first()
    if marina_map is None:
        marina_map = MarinaMap(marina_id=marina.id, name="Main marina map", image_url="/static/marina-map-demo.svg", width=1000, height=620)
        db.add(marina_map)
        db.flush()
    berth_id = int(form["berth_slot_id"])
    berth = db.get(BerthSlot, berth_id)
    if berth is None or berth.marina_id != marina.id:
        raise HTTPException(status_code=404, detail="Posto barca non trovato")
    position = (
        db.query(BerthPosition)
        .filter(BerthPosition.marina_map_id == marina_map.id, BerthPosition.berth_slot_id == berth.id)
        .first()
    )
    if position is None:
        position = BerthPosition(marina_map_id=marina_map.id, berth_slot_id=berth.id)
        db.add(position)
    position.x = int(form["x"])
    position.y = int(form["y"])
    position.w = int(form["w"])
    position.h = int(form["h"])
    db.commit()
    return _admin_redirect()


@router.post("/admin/map/positions")
async def update_admin_map_positions(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    form = await request.form()
    marina_map = db.query(MarinaMap).filter(MarinaMap.marina_id == marina.id).first()
    if marina_map is None:
        return _admin_redirect()
    positions = db.query(BerthPosition).filter(BerthPosition.marina_map_id == marina_map.id).all()
    for position in positions:
        position.x = int(form.get(f"position_{position.id}_x") or position.x)
        position.y = int(form.get(f"position_{position.id}_y") or position.y)
        position.w = int(form.get(f"position_{position.id}_w") or position.w)
        position.h = int(form.get(f"position_{position.id}_h") or position.h)
    db.commit()
    return _admin_redirect()


@router.post("/admin/map/layout")
async def update_admin_map_layout(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    form = await request.form()
    marina_map = db.query(MarinaMap).filter(MarinaMap.marina_id == marina.id).first()
    if marina_map is None:
        return RedirectResponse("/map?error=Mappa non trovata", status_code=303)

    raw_layout = str(form.get("layout_payload") or "").strip()
    raw_removed = str(form.get("removed_ids") or "").strip()
    if not raw_layout:
        return RedirectResponse("/map?error=Nessuna posizione da salvare", status_code=303)

    try:
        import json

        layout_items = json.loads(raw_layout)
        removed_ids = {int(item) for item in json.loads(raw_removed)} if raw_removed else set()
    except Exception:
        return RedirectResponse("/map?error=Formato layout non valido", status_code=303)

    existing_positions = {
        position.berth_slot_id: position
        for position in db.query(BerthPosition).filter(BerthPosition.marina_map_id == marina_map.id).all()
    }

    for berth_id in removed_ids:
        position = existing_positions.get(berth_id)
        if position is not None:
            db.delete(position)

    for item in layout_items:
        berth_id = int(item.get("berth_slot_id") or 0)
        berth = db.get(BerthSlot, berth_id)
        if berth is None or berth.marina_id != marina.id:
            continue
        position = existing_positions.get(berth_id)
        if position is None:
            position = BerthPosition(marina_map_id=marina_map.id, berth_slot_id=berth_id)
            db.add(position)
        position.x = max(0, int(item.get("x") or 0))
        position.y = max(0, int(item.get("y") or 0))
        position.w = max(18, int(item.get("w") or 18))
        position.h = max(18, int(item.get("h") or 18))

    db.commit()
    return _map_redirect()


@router.post("/admin/services")
async def create_admin_service(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    form = await request.form()
    db.add(
        MarinaService(
            marina_id=marina.id,
            code=str(form.get("code") or "").strip(),
            name=str(form.get("name") or "").strip(),
            description=str(form.get("description") or "").strip() or None,
            category=str(form.get("category") or "general").strip(),
            customer_visible=form.get("customer_visible") == "1",
            active=form.get("active") == "1",
        )
    )
    db.commit()
    return _admin_redirect()


@router.post("/admin/zones")
async def create_admin_zone(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    form = await request.form()
    db.add(
        MarinaZone(
            marina_id=marina.id,
            name=str(form.get("name") or "").strip(),
            zone_type=str(form.get("zone_type") or "general").strip(),
            color=str(form.get("color") or "#007c74").strip(),
            description=str(form.get("description") or "").strip() or None,
            customer_visible=form.get("customer_visible") == "1",
            sort_order=_form_int(form.get("sort_order"), 0),
        )
    )
    db.commit()
    return _admin_redirect()


@router.post("/admin/photos")
async def create_admin_photo(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    form = await request.form()
    db.add(
        MarinaPhoto(
            marina_id=marina.id,
            title=str(form.get("title") or "").strip(),
            image_url=str(form.get("image_url") or "").strip(),
            sort_order=_form_int(form.get("sort_order"), 0),
            active=form.get("active") == "1",
        )
    )
    db.commit()
    return _admin_redirect()


@router.post("/admin/extra-services")
async def create_admin_extra_service(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    form = await request.form()
    db.add(
        ExtraService(
            marina_id=marina.id,
            code=str(form.get("code") or "").strip(),
            name=str(form.get("name") or "").strip(),
            description=str(form.get("description") or "").strip() or None,
            billing_mode=str(form.get("billing_mode") or "per_booking").strip(),
            amount=_form_float(form.get("amount")),
            customer_visible=form.get("customer_visible") == "1",
            active=form.get("active") == "1",
            requires_staff_approval=form.get("requires_staff_approval") == "1",
        )
    )
    db.commit()
    return _admin_redirect()


@router.post("/admin/seasonal-rates")
async def create_admin_seasonal_rate(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    form = await request.form()
    zone_id_raw = str(form.get("zone_id") or "").strip()
    berth_category_raw = str(form.get("berth_category") or "").strip()
    db.add(
        SeasonalRate(
            marina_id=marina.id,
            zone_id=int(zone_id_raw) if zone_id_raw else None,
            name=str(form.get("name") or "").strip(),
            berth_category=berth_category_raw or None,
            start_month=_form_int(form.get("start_month"), 1),
            start_day=_form_int(form.get("start_day"), 1),
            end_month=_form_int(form.get("end_month"), 12),
            end_day=_form_int(form.get("end_day"), 31),
            day_multiplier=_form_float(form.get("day_multiplier") or 1),
            week_multiplier=_form_float(form.get("week_multiplier") or 1),
            month_multiplier=_form_float(form.get("month_multiplier") or 1),
            active=form.get("active") == "1",
        )
    )
    db.commit()
    return _admin_redirect()


@router.get("/admin/bookings")
def admin_bookings_page(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    bookings = (
        db.query(Booking)
        .options(
            joinedload(Booking.user),
            joinedload(Booking.boat),
            joinedload(Booking.berth_slot),
            joinedload(Booking.extra_services).joinedload(BookingExtraService.extra_service),
        )
    )
    if user.role in {"marina_admin", "staff"}:
        bookings = bookings.filter(Booking.marina_id == user.marina_id)
    bookings = bookings.order_by(Booking.start_date.desc(), Booking.id.desc()).all()
    waitlist_requests = (
        db.query(WaitlistRequest)
        .filter(WaitlistRequest.marina_id == marina.id)
        .order_by(WaitlistRequest.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        request,
        "admin_bookings.html",
        _ctx(request, user, marina=marina, bookings=bookings, waitlist_requests=waitlist_requests),
    )


@router.get("/customer")
def customer_dashboard(request: Request, db: Session = Depends(get_db)):
    user = _require_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    settings = _get_or_create_settings(db, marina)
    boats = db.query(Boat).filter(Boat.user_id == user.id).order_by(Boat.created_at.desc()).all()
    bookings = booking_service.list_bookings(db, user)
    available_berths = berth_service.list_berths(db, marina.id if marina else None)
    return templates.TemplateResponse(
        request,
        "customer_dashboard.html",
        _ctx(
            request,
            user,
            marina=marina,
            settings=settings,
            boats=boats,
            bookings=bookings,
            available_berths=[berth for berth in available_berths if berth.status == "available"],
        ),
    )


@router.get("/ui/berths")
def berths_page(request: Request, db: Session = Depends(get_db)):
    user = _require_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    if user.role == "customer":
        return RedirectResponse("/ui/bookings", status_code=303)
    marina = _main_marina(db, user)
    berths = berth_service.list_berths(db, marina.id if marina else None)
    zones = db.query(MarinaZone).filter(MarinaZone.marina_id == marina.id).order_by(MarinaZone.sort_order, MarinaZone.name).all()
    return templates.TemplateResponse(request, "berths.html", _ctx(request, user, marina=marina, berths=berths, zones=zones, error=None))


@router.post("/ui/berths")
async def create_berth_page(request: Request, db: Session = Depends(get_db)):
    user = _require_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    if user.role == "customer":
        return RedirectResponse("/ui/bookings", status_code=303)
    form = await request.form()
    try:
        payload = BerthSlotCreate(
            marina_id=int(form["marina_id"]),
            zone_id=int(form["zone_id"]) if form.get("zone_id") else None,
            code=str(form["code"]).strip(),
            max_length_m=float(form["max_length_m"]),
            max_beam_m=float(form["max_beam_m"]),
            max_draft_m=float(form["max_draft_m"]),
            category=str(form["category"]),
            usage_type=str(form.get("usage_type") or "transient"),
            price_per_day=float(form["price_per_day"]),
            price_per_week=float(form["price_per_week"]),
            price_per_month=float(form["price_per_month"]),
            status=str(form.get("status") or "available"),
            special_approval_required=form.get("special_approval_required") == "1",
            notes=str(form.get("notes") or ""),
        )
        if user.role not in {"super_admin", "marina_admin", "staff"}:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        berth_service.create_berth(db, payload)
        return RedirectResponse("/ui/berths", status_code=303)
    except Exception as exc:
        marina = _main_marina(db, user)
        berths = berth_service.list_berths(db, marina.id if marina else None)
        zones = db.query(MarinaZone).filter(MarinaZone.marina_id == marina.id).order_by(MarinaZone.sort_order, MarinaZone.name).all()
        detail = exc.detail if isinstance(exc, HTTPException) else str(exc)
        return templates.TemplateResponse(request, "berths.html", _ctx(request, user, marina=marina, berths=berths, zones=zones, error=detail))


@router.get("/ui/boats")
def boats_page(request: Request, db: Session = Depends(get_db)):
    user = _require_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    boat_filter = Boat.user_id == user.id if user.role == "customer" else Boat.marina_id == marina.id
    boats = db.query(Boat).filter(boat_filter).all()
    return templates.TemplateResponse(request, "boats.html", _ctx(request, user, marina=marina, boats=boats, error=None))


@router.post("/ui/boats")
async def create_boat_page(request: Request, db: Session = Depends(get_db)):
    user = _require_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    form = await request.form()
    marina = _main_marina(db, user)
    payload = BoatCreate(
        user_id=user.id,
        marina_id=marina.id,
        name=str(form["name"]).strip(),
        boat_type=str(form["boat_type"]).strip() or "other",
        length_m=float(form["length_m"]),
        beam_m=float(form["beam_m"]),
        draft_m=float(form["draft_m"]),
        engine_power_hp=int(form["engine_power_hp"]) if form.get("engine_power_hp") else None,
        registration_code=str(form.get("registration_code") or ""),
        insurance_notes=str(form.get("insurance_notes") or ""),
        notes=str(form.get("notes") or ""),
    )
    boat = Boat(**payload.model_dump())
    db.add(boat)
    db.commit()
    return RedirectResponse("/ui/boats", status_code=303)


@router.get("/ui/bookings")
def bookings_page(request: Request, db: Session = Depends(get_db)):
    user = _require_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    settings = _get_or_create_settings(db, marina)
    bookings = booking_service.list_bookings(db, user)
    waitlist_requests = booking_service.list_waitlist_requests(db, user)
    boat_filter = Boat.user_id == user.id if user.role == "customer" else Boat.marina_id == marina.id
    boats = db.query(Boat).filter(boat_filter).all()
    users = db.query(User).filter(User.marina_id == marina.id, User.role == "customer").all() if user.role != "customer" else [user]
    berths = [
        berth
        for berth in berth_service.list_berths(db, marina.id)
        if berth.status == "available" and berth.usage_type == "transient"
    ]
    availability_bookings = (
        db.query(Booking)
        .filter(Booking.marina_id == marina.id, Booking.status.in_(["pending", "confirmed"]))
        .all()
    )
    marina_map = (
        db.query(MarinaMap)
        .options(joinedload(MarinaMap.berth_positions).joinedload(BerthPosition.berth_slot))
        .filter(MarinaMap.marina_id == marina.id)
        .first()
    )
    services = marina_profile_service.list_visible_services(db, marina.id)
    zones = marina_profile_service.list_visible_zones(db, marina.id)
    extra_services = marina_profile_service.list_bookable_extra_services(db, marina.id)
    photos = marina_profile_service.list_visible_photos(db, marina.id)
    highlighted_booking = None
    show_booking = str(request.query_params.get("show_booking") or "").strip()
    if show_booking:
        try:
            highlighted_booking = _get_accessible_booking(db, int(show_booking), user)
        except (HTTPException, ValueError):
            highlighted_booking = None
    return templates.TemplateResponse(
        request,
        "bookings.html",
        _ctx(
            request,
            user,
            marina=marina,
            settings=settings,
            bookings=bookings,
            boats=boats,
            users=users,
            berths=berths,
            services=services,
            zones=zones,
            photos=photos,
            extra_services=extra_services,
            waitlist_requests=waitlist_requests,
            availability_bookings=availability_bookings,
            marina_map=marina_map,
            highlighted_booking=highlighted_booking,
            saved=request.query_params.get("saved") == "1",
            error=request.query_params.get("error"),
        ),
    )


@router.post("/ui/bookings")
async def create_booking_page(request: Request, db: Session = Depends(get_db)):
    user = _require_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    form = await request.form()
    marina = _main_marina(db, user)
    settings = _get_or_create_settings(db, marina)
    try:
        booking_user_id = user.id if user.role == "customer" else int(form["user_id"])
        berth_slot_id_raw = str(form.get("berth_slot_id") or "").strip()
        start_date_raw = str(form.get("start_date") or "").strip()
        end_date_raw = str(form.get("end_date") or "").strip()
        if not berth_slot_id_raw:
            raise HTTPException(status_code=400, detail="Scegli un posto barca sulla mappa prima di confermare.")
        if not start_date_raw or not end_date_raw:
            raise HTTPException(status_code=400, detail="Scegli data di inizio e data di fine dal calendario.")
        try:
            berth_slot_id = int(berth_slot_id_raw)
            start_date = date.fromisoformat(start_date_raw)
            end_date = date.fromisoformat(end_date_raw)
        except ValueError:
            raise HTTPException(status_code=400, detail="Controlla posto barca e date selezionate.")
        if end_date <= start_date:
            raise HTTPException(status_code=400, detail="La data di fine deve essere successiva alla data di inizio.")

        boat_id = str(form.get("boat_id") or "").strip()
        if boat_id:
            selected_boat_id = int(boat_id)
        else:
            boat_name = str(form.get("boat_name") or "").strip()
            if not boat_name:
                raise HTTPException(status_code=400, detail="Scrivi il nome della barca.")
            try:
                length_m = _form_float(form.get("length_m"))
                beam_m = _form_float(form.get("beam_m"))
                draft_m = _form_float(form.get("draft_m"))
            except ValueError:
                raise HTTPException(status_code=400, detail="Inserisci misure numeriche valide per lunghezza, larghezza e pescaggio.")
            boat = Boat(
                user_id=booking_user_id,
                marina_id=marina.id,
                name=boat_name,
                boat_type=str(form.get("boat_type") or "other").strip() or "other",
                length_m=length_m,
                beam_m=beam_m,
                draft_m=draft_m,
                notes="Created from booking flow",
            )
            db.add(boat)
            db.flush()
            selected_boat_id = boat.id

        extra_service_requests = []
        for service in marina_profile_service.list_bookable_extra_services(db, marina.id):
            if form.get(f"extra_service_{service.id}") != "1":
                continue
            extra_service_requests.append(
                {
                    "service_id": service.id,
                    "quantity": _form_int(form.get(f"extra_service_quantity_{service.id}"), 1),
                }
            )

        payload = BookingCreate(
            marina_id=marina.id,
            user_id=booking_user_id,
            berth_slot_id=berth_slot_id,
            boat_id=selected_boat_id,
            start_date=start_date,
            end_date=end_date,
            currency=marina.default_currency,
            arrival_time=settings.check_in_start,
            departure_time=settings.check_out_time,
            notes=str(form.get("notes") or ""),
        )
        booking = booking_service.create_booking(db, payload, user, extra_service_requests=extra_service_requests)
        return RedirectResponse(f"/ui/checkout/{booking.id}", status_code=303)
    except Exception as exc:
        db.rollback()
        bookings = booking_service.list_bookings(db, user)
        boat_filter = Boat.user_id == user.id if user.role == "customer" else Boat.marina_id == marina.id
        boats = db.query(Boat).filter(boat_filter).all()
        users = db.query(User).filter(User.marina_id == marina.id, User.role == "customer").all() if user.role != "customer" else [user]
        berths = [
            berth
            for berth in berth_service.list_berths(db, marina.id)
            if berth.status == "available" and berth.usage_type == "transient"
        ]
        services = marina_profile_service.list_visible_services(db, marina.id)
        zones = marina_profile_service.list_visible_zones(db, marina.id)
        extra_services = marina_profile_service.list_bookable_extra_services(db, marina.id)
        photos = marina_profile_service.list_visible_photos(db, marina.id)
        waitlist_requests = booking_service.list_waitlist_requests(db, user)
        availability_bookings = (
            db.query(Booking)
            .filter(Booking.marina_id == marina.id, Booking.status.in_(["pending", "confirmed"]))
            .all()
        )
        marina_map = (
            db.query(MarinaMap)
            .options(joinedload(MarinaMap.berth_positions).joinedload(BerthPosition.berth_slot))
            .filter(MarinaMap.marina_id == marina.id)
            .first()
        )
        detail = exc.detail if isinstance(exc, HTTPException) else str(exc)
        return templates.TemplateResponse(
            request,
            "bookings.html",
            _ctx(
                request,
                user,
                marina=marina,
                settings=settings,
                bookings=bookings,
                boats=boats,
                users=users,
                berths=berths,
                services=services,
                zones=zones,
                photos=photos,
                extra_services=extra_services,
                waitlist_requests=waitlist_requests,
                availability_bookings=availability_bookings,
                marina_map=marina_map,
                highlighted_booking=None,
                error=detail,
            ),
        )


@router.post("/ui/waitlist")
async def create_waitlist_page(request: Request, db: Session = Depends(get_db)):
    user = _require_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    form = await request.form()
    try:
        payload = WaitlistRequestCreate(
            marina_id=marina.id,
            user_id=user.id if user.role == "customer" else int(form.get("user_id") or user.id),
            zone_id=int(form.get("zone_id")) if form.get("zone_id") else None,
            boat_name=str(form.get("boat_name") or "").strip(),
            boat_type=str(form.get("boat_type") or "other").strip(),
            length_m=_form_float(form.get("length_m")),
            beam_m=_form_float(form.get("beam_m")),
            draft_m=_form_float(form.get("draft_m")),
            desired_start_date=date.fromisoformat(str(form.get("start_date") or "").strip()),
            desired_end_date=date.fromisoformat(str(form.get("end_date") or "").strip()),
            notes=str(form.get("notes") or "").strip() or None,
        )
        booking_service.create_waitlist_request(db, payload, user)
        return RedirectResponse("/ui/bookings?saved=1", status_code=303)
    except Exception as exc:
        detail = exc.detail if isinstance(exc, HTTPException) else str(exc)
        return RedirectResponse(f"/ui/bookings?error={detail}", status_code=303)


@router.post("/ui/pay/{booking_id}")
async def pay_booking_page(booking_id: int, request: Request, db: Session = Depends(get_db)):
    user = _require_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    form = await request.form()
    method = str(form.get("payment_method") or "card")
    if method == "card":
        cardholder_name = str(form.get("cardholder_name") or "").strip()
        card_number = "".join(ch for ch in str(form.get("card_number") or "") if ch.isdigit())
        expiry = str(form.get("card_expiry") or "").strip()
        if not cardholder_name or len(card_number) < 12 or not expiry:
            return RedirectResponse(f"/ui/checkout/{booking_id}?error=card", status_code=303)
        reference = f"mock_card_paid_last4_{card_number[-4:]}"
        provider = "mock_card"
    elif method == "bank_transfer":
        holder = str(form.get("bank_holder") or "").strip()
        transfer_reference = str(form.get("transfer_reference") or "").strip()
        transfer_date = str(form.get("transfer_date") or "").strip()
        if not holder or not transfer_reference or not transfer_date:
            return RedirectResponse(f"/ui/checkout/{booking_id}?error=bank", status_code=303)
        reference = f"mock_bank_transfer_{transfer_reference}"
        provider = "mock_bank_transfer"
    else:
        return RedirectResponse(f"/ui/checkout/{booking_id}?error=method", status_code=303)

    payment_service.mock_checkout(db, booking_id, user, provider=provider, payment_reference=reference)
    return RedirectResponse(f"/ui/checkout/{booking_id}?paid=1", status_code=303)


@router.get("/ui/checkout/{booking_id}")
def checkout_page(booking_id: int, request: Request, db: Session = Depends(get_db)):
    user = _require_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    booking = _get_accessible_booking(db, booking_id, user)
    settings = _get_or_create_settings(db, booking.marina)
    payments = payment_service.list_payments(db, user)
    booking_payments = [payment for payment in payments if payment.booking_id == booking.id]
    return templates.TemplateResponse(
        request,
        "checkout.html",
        _ctx(
            request,
            user,
            booking=booking,
            settings=settings,
            payment=booking_payments[0] if booking_payments else None,
            paid=request.query_params.get("paid") == "1",
            error=request.query_params.get("error"),
        ),
    )


@router.get("/ui/receipt/{booking_id}")
def receipt_page(booking_id: int, request: Request, db: Session = Depends(get_db)):
    user = _require_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    booking = _get_accessible_booking(db, booking_id, user)
    settings = _get_or_create_settings(db, booking.marina)
    payments = payment_service.list_payments(db, user)
    booking_payments = [payment for payment in payments if payment.booking_id == booking.id]
    return templates.TemplateResponse(
        request,
        "receipt.html",
        _ctx(
            request,
            user,
            booking=booking,
            settings=settings,
            payment=booking_payments[0] if booking_payments else None,
        ),
    )


@router.get("/map")
def map_page(request: Request, db: Session = Depends(get_db)):
    user = _require_admin_user(request, db)
    if isinstance(user, RedirectResponse):
        return user
    marina = _main_marina(db, user)
    marina_map = (
        db.query(MarinaMap)
        .options(joinedload(MarinaMap.berth_positions).joinedload(BerthPosition.berth_slot))
        .filter(MarinaMap.marina_id == marina.id)
        .first()
    )
    berths = berth_service.list_berths(db, marina.id)
    zones = db.query(MarinaZone).filter(MarinaZone.marina_id == marina.id).order_by(MarinaZone.sort_order, MarinaZone.name).all()
    return templates.TemplateResponse(
        request,
        "map.html",
        _ctx(
            request,
            user,
            marina=marina,
            marina_map=marina_map,
            berths=berths,
            zones=zones,
            saved=request.query_params.get("saved") == "1",
            error=request.query_params.get("error"),
        ),
    )
