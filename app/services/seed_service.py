from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.auth.password import hash_password
from app.models.berth import BerthSlot
from app.models.boat import Boat
from app.models.booking import Booking
from app.models.extra_service import ExtraService
from app.models.marina import Marina
from app.models.marina_map import BerthPosition, MarinaMap
from app.models.marina_photo import MarinaPhoto
from app.models.marina_service import MarinaService
from app.models.marina_settings import MarinaSettings
from app.models.marina_zone import MarinaZone
from app.models.payment import Payment
from app.models.seasonal_rate import SeasonalRate
from app.models.subscription import MarinaSubscription, SubscriptionPlan
from app.models.user import User


DEMO_PASSWORD = "Demo12345!"


def seed_demo_data(db: Session) -> None:
    if db.query(SubscriptionPlan).count() == 0:
        free = SubscriptionPlan(
            name="free",
            price_monthly=0,
            currency="EUR",
            max_berths=10,
            max_staff_users=1,
            allow_map=False,
            allow_payments=False,
            allow_advanced_dashboard=False,
            active=True,
        )
        pro = SubscriptionPlan(
            name="pro",
            price_monthly=79,
            currency="EUR",
            max_berths=100,
            max_staff_users=5,
            allow_map=True,
            allow_payments=True,
            allow_advanced_dashboard=True,
            active=True,
        )
        premium = SubscriptionPlan(
            name="premium",
            price_monthly=199,
            currency="EUR",
            max_berths=500,
            max_staff_users=-1,
            allow_map=True,
            allow_payments=True,
            allow_advanced_dashboard=True,
            active=True,
        )
        db.add_all([free, pro, premium])
        db.flush()
    else:
        pro = db.query(SubscriptionPlan).filter(SubscriptionPlan.name == "pro").first()

    marina = db.query(Marina).filter(Marina.name == "Demo Marina International").first()
    if marina is None:
        marina = Marina(
            name="Demo Marina International",
            country="Italy",
            city="Venice",
            address="North Basin 12",
            structure_type="marina",
            timezone="Europe/Rome",
            default_currency="EUR",
            public_slug="demo-marina-international",
            short_description="Porto turistico demo con posti occasionali, servizi, cantiere e mappa interattiva.",
            long_description="Demo Marina International mostra come una darsena, un circolo nautico o un piccolo porto possano pubblicare servizi, regole, foto, zone e posti prenotabili in tempo reale.",
            latitude=45.4371,
            longitude=12.3326,
            active=True,
            subscription_plan_id=pro.id,
        )
        db.add(marina)
        db.flush()
    else:
        marina.structure_type = marina.structure_type or "marina"
        marina.public_slug = marina.public_slug or "demo-marina-international"
        marina.short_description = marina.short_description or "Porto turistico demo con posti occasionali, servizi, cantiere e mappa interattiva."
        marina.long_description = marina.long_description or "Demo Marina International mostra come una darsena, un circolo nautico o un piccolo porto possano pubblicare servizi, regole, foto, zone e posti prenotabili in tempo reale."
        marina.latitude = marina.latitude or 45.4371
        marina.longitude = marina.longitude or 12.3326

    if not db.query(MarinaSubscription).filter(MarinaSubscription.marina_id == marina.id).first():
        db.add(
            MarinaSubscription(
                marina_id=marina.id,
                subscription_plan_id=pro.id,
                status="active",
                start_date=date.today(),
                stripe_customer_id="cus_demo_ready",
                stripe_subscription_id="sub_demo_ready",
            )
        )

    _seed_users(db, marina)
    _seed_settings(db, marina)
    zones = _seed_zones(db, marina)
    berths = _seed_berths(db, marina)
    customer = db.query(User).filter(User.email == "customer@marinasuite.demo").first()
    boats = _seed_boats(db, marina, customer)
    _seed_bookings_and_payment(db, marina, customer, berths, boats)
    _seed_map(db, marina, berths)
    _seed_services(db, marina)
    _seed_photos(db, marina)
    _seed_extra_services(db, marina)
    _seed_seasonal_rates(db, marina, zones)
    _assign_demo_zone_metadata(db, marina, berths, zones)
    db.commit()


def _seed_users(db: Session, marina: Marina) -> None:
    users = [
        {
            "marina_id": None,
            "full_name": "SaaS Super Admin",
            "email": "super@marinasuite.demo",
            "role": "super_admin",
            "phone": "+390000000001",
            "language_preference": "it",
        },
        {
            "marina_id": marina.id,
            "full_name": "Marina Admin Demo",
            "email": "admin@marinasuite.demo",
            "role": "marina_admin",
            "phone": "+390000000002",
            "language_preference": "it",
        },
        {
            "marina_id": marina.id,
            "full_name": "Staff Member Demo",
            "email": "staff@marinasuite.demo",
            "role": "staff",
            "phone": "+390000000003",
            "language_preference": "it",
        },
        {
            "marina_id": marina.id,
            "full_name": "Customer Demo",
            "email": "customer@marinasuite.demo",
            "role": "customer",
            "phone": "+390000000004",
            "language_preference": "it",
        },
    ]
    for item in users:
        if not db.query(User).filter(User.email == item["email"]).first():
            db.add(
                User(
                    **item,
                    password_hash=hash_password(DEMO_PASSWORD),
                    currency_preference="EUR",
                    is_active=True,
                )
            )
    db.flush()


def _seed_settings(db: Session, marina: Marina) -> None:
    settings = db.query(MarinaSettings).filter(MarinaSettings.marina_id == marina.id).first()
    if settings is None:
        settings = MarinaSettings(
            marina_id=marina.id,
            office_email="info@demomarina.example",
            office_phone="+39 041 000 000",
            emergency_phone="+39 333 000 000",
            vhf_channel="VHF 09",
            opening_hours="Lun-Dom 08:00-20:00",
            check_in_start="09:00",
            check_in_end="18:00",
            check_out_time="11:00",
            booking_terms="Presentarsi in banchina con ricevuta e documento. Le manovre restano sotto responsabilita dello skipper.",
            rules_pdf_url=None,
            map_notes="La mappa demo contiene posti di categoria e dimensioni miste, pensati per simulare una darsena reale.",
            nautical_access_notes="Ingresso consigliato dal canale Nord. Prestare attenzione al traffico locale, alle raffiche laterali e alle manovre in zona fuel dock.",
            seabed_notes="Fondale variabile tra 1.8 m e 4.2 m nelle aree operative. I posti in cantiere e servizi hanno limitazioni temporanee.",
            accepts_catamarans=True,
            accepts_multihulls=True,
        )
        db.add(settings)
    else:
        settings.office_email = settings.office_email or "info@demomarina.example"
        settings.office_phone = settings.office_phone or "+39 041 000 000"
        settings.emergency_phone = settings.emergency_phone or "+39 333 000 000"
        settings.vhf_channel = settings.vhf_channel or "VHF 09"
        settings.opening_hours = settings.opening_hours or "Lun-Dom 08:00-20:00"
        settings.check_in_start = settings.check_in_start or "09:00"
        settings.check_in_end = settings.check_in_end or "18:00"
        settings.check_out_time = settings.check_out_time or "11:00"
        settings.booking_terms = settings.booking_terms or "Presentarsi in banchina con ricevuta e documento. Le manovre restano sotto responsabilita dello skipper."
        settings.map_notes = settings.map_notes or "La mappa demo contiene posti di categoria e dimensioni miste, pensati per simulare una darsena reale."
        settings.nautical_access_notes = settings.nautical_access_notes or "Ingresso consigliato dal canale Nord. Prestare attenzione al traffico locale, alle raffiche laterali e alle manovre in zona fuel dock."
        settings.seabed_notes = settings.seabed_notes or "Fondale variabile tra 1.8 m e 4.2 m nelle aree operative. I posti in cantiere e servizi hanno limitazioni temporanee."
    db.flush()


def _seed_zones(db: Session, marina: Marina) -> list[MarinaZone]:
    existing = db.query(MarinaZone).filter(MarinaZone.marina_id == marina.id).all()
    if existing:
        return existing
    zones = [
        MarinaZone(marina_id=marina.id, name="Posti occasionali", zone_type="transient", color="#2f8f5b", description="Area dedicata ai transiti e agli arrivi brevi.", sort_order=1),
        MarinaZone(marina_id=marina.id, name="Pontili armatori", zone_type="owner", color="#2f6bb2", description="Pontili riservati ai posti annuali e stagionali.", sort_order=2),
        MarinaZone(marina_id=marina.id, name="Cantiere e servizi", zone_type="service", color="#7a5c00", description="Area per manutenzioni, travel lift, fuel dock e manovre operative.", sort_order=3),
    ]
    db.add_all(zones)
    db.flush()
    return zones


def _seed_berths(db: Session, marina: Marina) -> list[BerthSlot]:
    existing = db.query(BerthSlot).filter(BerthSlot.marina_id == marina.id).all()
    if existing:
        return existing
    data = _complex_demo_berths()
    berths = [
        BerthSlot(
            marina_id=marina.id,
            code=code,
            max_length_m=max_length,
            max_beam_m=max_beam,
            max_draft_m=max_draft,
            category=category,
            usage_type=usage_type,
            price_per_day=day,
            price_per_week=week,
            price_per_month=month,
            status=status,
            special_approval_required=False,
            notes=notes,
            active=True,
        )
        for code, max_length, max_beam, max_draft, category, usage_type, day, week, month, status, notes in data
    ]
    db.add_all(berths)
    db.flush()
    return berths


def _dimension_for_category(category: str, tier: int) -> tuple[float, float, float, int, int, int]:
    presets = {
        "sail": [(9.5, 3.2, 1.8, 35, 210, 720), (12.0, 3.8, 2.2, 48, 288, 980), (15.0, 4.6, 2.8, 72, 432, 1480)],
        "motor": [(8.5, 3.0, 1.2, 34, 204, 690), (12.5, 4.0, 1.6, 54, 324, 1120), (16.0, 5.0, 2.0, 84, 504, 1720)],
        "catamaran": [(12.0, 6.0, 1.6, 76, 456, 1540), (16.0, 7.4, 2.0, 108, 648, 2220), (20.0, 8.8, 2.4, 148, 888, 2980)],
        "other": [(7.5, 2.6, 1.0, 26, 156, 520), (11.0, 3.6, 1.4, 42, 252, 860), (14.0, 4.4, 1.8, 62, 372, 1280)],
    }
    return presets[category][tier % len(presets[category])]


def _complex_demo_berths() -> list[tuple[str, float, float, float, str, str, int, int, int, str, str]]:
    data = []
    transient_categories = ["sail", "motor", "sail", "motor", "catamaran", "other"]
    for index in range(1, 21):
        category = transient_categories[(index - 1) % len(transient_categories)]
        max_length, max_beam, max_draft, day, week, month = _dimension_for_category(category, index)
        data.append(
            (
                f"O{index:02d}",
                max_length,
                max_beam,
                max_draft,
                category,
                "transient",
                day,
                week,
                month,
                "available",
                "Demo occasional berth: bookable by visiting customers.",
            )
        )

    owner_categories = ["sail", "motor", "sail", "motor", "catamaran", "sail", "motor"]
    for index in range(1, 71):
        category = owner_categories[(index - 1) % len(owner_categories)]
        max_length, max_beam, max_draft, day, week, month = _dimension_for_category(category, index + 1)
        data.append(
            (
                f"A{index:03d}",
                max_length,
                max_beam,
                max_draft,
                category,
                "owner",
                day,
                week,
                month,
                "occupied",
                "Demo owner berth: reserved for annual berth holders.",
            )
        )

    service_categories = ["motor", "other", "sail", "other", "catamaran"]
    for index in range(1, 11):
        category = service_categories[(index - 1) % len(service_categories)]
        max_length, max_beam, max_draft, day, week, month = _dimension_for_category(category, index + 2)
        data.append(
            (
                f"M{index:02d}",
                max_length,
                max_beam,
                max_draft,
                category,
                "service",
                day,
                week,
                month,
                "maintenance",
                "Demo service berth: reserved for maintenance, yard work, or operational needs.",
            )
        )
    return data


def _seed_boats(db: Session, marina: Marina, customer: User) -> list[Boat]:
    existing = db.query(Boat).filter(Boat.marina_id == marina.id).all()
    if existing:
        return existing
    boats = [
        Boat(
            user_id=customer.id,
            marina_id=marina.id,
            name="Blue Mistral",
            boat_type="sail",
            length_m=8.6,
            beam_m=3.0,
            draft_m=1.6,
            engine_power_hp=29,
            registration_code="IT-DEMO-001",
            insurance_notes="Demo insurance valid",
        ),
        Boat(
            user_id=customer.id,
            marina_id=marina.id,
            name="Silver Tide",
            boat_type="motor",
            length_m=10.8,
            beam_m=3.5,
            draft_m=1.4,
            engine_power_hp=220,
            registration_code="IT-DEMO-002",
            insurance_notes="Demo insurance valid",
        ),
    ]
    db.add_all(boats)
    db.flush()
    return boats


def _seed_bookings_and_payment(
    db: Session,
    marina: Marina,
    customer: User,
    berths: list[BerthSlot],
    boats: list[Boat],
) -> None:
    if db.query(Booking).filter(Booking.marina_id == marina.id).count():
        return
    today = date.today()
    berth_by_code = {berth.code: berth for berth in berths}
    bookings = [
        Booking(
            marina_id=marina.id,
            user_id=customer.id,
            berth_slot_id=berth_by_code["O01"].id,
            boat_id=boats[0].id,
            start_date=today + timedelta(days=3),
            end_date=today + timedelta(days=6),
            total_price=105,
            currency="EUR",
            status="pending",
            payment_status="unpaid",
            notes="Demo pending booking",
        ),
        Booking(
            marina_id=marina.id,
            user_id=customer.id,
            berth_slot_id=berth_by_code["O04"].id,
            boat_id=boats[1].id,
            start_date=today + timedelta(days=12),
            end_date=today + timedelta(days=17),
            total_price=350,
            currency="EUR",
            status="confirmed",
            payment_status="paid",
            notes="Demo paid booking",
        ),
        Booking(
            marina_id=marina.id,
            user_id=customer.id,
            berth_slot_id=berth_by_code["O10"].id,
            boat_id=boats[1].id,
            start_date=today - timedelta(days=20),
            end_date=today - timedelta(days=14),
            total_price=348,
            currency="EUR",
            status="completed",
            payment_status="paid",
            notes="Demo completed booking",
        ),
    ]
    db.add_all(bookings)
    db.flush()
    db.add(
        Payment(
            marina_id=marina.id,
            booking_id=bookings[1].id,
            provider="mock",
            amount=bookings[1].total_price,
            currency="EUR",
            status="paid",
            provider_reference="mock_stripe_ready_seed",
        )
    )


def _seed_map(db: Session, marina: Marina, berths: list[BerthSlot]) -> None:
    if db.query(MarinaMap).filter(MarinaMap.marina_id == marina.id).first():
        return
    marina_map = MarinaMap(
        marina_id=marina.id,
        name="Complex Demo Marina Map",
        image_url="/static/marina-map-demo.svg",
        width=1400,
        height=900,
    )
    db.add(marina_map)
    db.flush()
    positions = _complex_demo_positions()
    berth_by_code = {berth.code: berth for berth in berths}
    db.add_all(
        [
            BerthPosition(
                marina_map_id=marina_map.id,
                berth_slot_id=berth_by_code[code].id,
                x=x,
                y=y,
                w=w,
                h=h,
            )
            for code, x, y, w, h in positions
            if code in berth_by_code
        ]
    )


def _seed_services(db: Session, marina: Marina) -> None:
    if db.query(MarinaService).filter(MarinaService.marina_id == marina.id).count():
        return
    services = [
        ("fuel", "Fuel dock", "Rifornimento carburante in banchina con assistenza staff.", "dock"),
        ("water", "Acqua in banchina", "Colonnine acqua disponibili sui pontili ospiti.", "dock"),
        ("power", "Corrente elettrica", "Allacci 16A e 32A su richiesta.", "dock"),
        ("showers", "Docce e servizi", "Servizi igienici e docce per equipaggi.", "guest"),
        ("laundry", "Lavanderia", "Zona lavanderia accessibile con badge ospite.", "guest"),
        ("parking", "Parcheggio", "Parcheggio auto nelle vicinanze della marina.", "guest"),
        ("travel_lift", "Travel lift", "Sollevamento e alaggio su prenotazione.", "yard"),
        ("yard", "Cantiere e officina", "Piccoli interventi tecnici e manutenzioni.", "yard"),
        ("restaurant", "Bar e ristorante", "Punto ristoro sul fronte mare.", "guest"),
        ("wifi", "Wi-Fi porto", "Connessione dedicata per ospiti e soci.", "guest"),
        ("pump_out", "Pump-out", "Servizio raccolta acque nere su richiesta.", "dock"),
        ("security", "Sicurezza", "Videosorveglianza, badge e assistenza arrivi.", "guest"),
    ]
    db.add_all(
        [
            MarinaService(
                marina_id=marina.id,
                code=code,
                name=name,
                description=description,
                category=category,
                customer_visible=True,
                active=True,
            )
            for code, name, description, category in services
        ]
    )


def _seed_photos(db: Session, marina: Marina) -> None:
    if db.query(MarinaPhoto).filter(MarinaPhoto.marina_id == marina.id).count():
        return
    photos = [
        ("Vista porto", "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1200&q=80", 1),
        ("Pontili ospiti", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80", 2),
        ("Area circolo e servizi", "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?auto=format&fit=crop&w=1200&q=80", 3),
    ]
    db.add_all(
        [
            MarinaPhoto(
                marina_id=marina.id,
                title=title,
                image_url=image_url,
                sort_order=sort_order,
                active=True,
            )
            for title, image_url, sort_order in photos
        ]
    )


def _seed_extra_services(db: Session, marina: Marina) -> None:
    if db.query(ExtraService).filter(ExtraService.marina_id == marina.id).count():
        return
    extras = [
        ("shore_power", "Corrente elettrica", "Allaccio elettrico dedicato al posto.", "per_day", 8, False),
        ("water_hookup", "Acqua in banchina", "Allaccio acqua per la durata della sosta.", "per_day", 4, False),
        ("parking_pass", "Pass parcheggio", "Pass auto area marina.", "per_booking", 18, False),
        ("late_checkout", "Late check-out", "Uscita estesa oltre l'orario standard.", "per_booking", 25, True),
        ("travel_lift_slot", "Finestra travel lift", "Assistenza cantiere e sollevamento.", "per_booking", 120, True),
    ]
    db.add_all(
        [
            ExtraService(
                marina_id=marina.id,
                code=code,
                name=name,
                description=description,
                billing_mode=billing_mode,
                amount=amount,
                customer_visible=True,
                active=True,
                requires_staff_approval=requires_staff_approval,
            )
            for code, name, description, billing_mode, amount, requires_staff_approval in extras
        ]
    )


def _seed_seasonal_rates(db: Session, marina: Marina, zones: list[MarinaZone]) -> None:
    if db.query(SeasonalRate).filter(SeasonalRate.marina_id == marina.id).count():
        return
    transient_zone = next((zone for zone in zones if zone.zone_type == "transient"), None)
    rates = [
        SeasonalRate(
            marina_id=marina.id,
            zone_id=transient_zone.id if transient_zone else None,
            name="Alta stagione estiva",
            berth_category=None,
            start_month=6,
            start_day=1,
            end_month=9,
            end_day=15,
            day_multiplier=1.15,
            week_multiplier=1.12,
            month_multiplier=1.08,
            active=True,
        ),
        SeasonalRate(
            marina_id=marina.id,
            zone_id=transient_zone.id if transient_zone else None,
            name="Weekend eventi e regate",
            berth_category="catamaran",
            start_month=9,
            start_day=16,
            end_month=10,
            end_day=15,
            day_multiplier=1.10,
            week_multiplier=1.08,
            month_multiplier=1.00,
            active=True,
        ),
    ]
    db.add_all(rates)


def _assign_demo_zone_metadata(db: Session, marina: Marina, berths: list[BerthSlot], zones: list[MarinaZone]) -> None:
    zone_by_type = {zone.zone_type: zone for zone in zones}
    for berth in berths:
        if berth.usage_type == "transient":
            berth.zone_id = zone_by_type.get("transient").id if zone_by_type.get("transient") else berth.zone_id
            berth.special_approval_required = berth.category == "catamaran" or float(berth.max_length_m) >= 16
        elif berth.usage_type == "owner":
            berth.zone_id = zone_by_type.get("owner").id if zone_by_type.get("owner") else berth.zone_id
            berth.special_approval_required = False
        elif berth.usage_type == "service":
            berth.zone_id = zone_by_type.get("service").id if zone_by_type.get("service") else berth.zone_id
            berth.special_approval_required = True


def _complex_demo_positions() -> list[tuple[str, int, int, int, int]]:
    positions = []

    # 20 visitor berths near the entrance quay.
    for index in range(1, 11):
        positions.append((f"O{index:02d}", 150 + (index - 1) * 54, 140, 38, 24))
    for index in range(11, 21):
        positions.append((f"O{index:02d}", 150 + (index - 11) * 54, 220, 38, 24))

    # 70 owner berths along five internal pontoons, 14 per pontoon.
    count = 1
    for y in [350, 440, 530, 620, 710]:
        for slot in range(14):
            positions.append((f"A{count:03d}", 160 + slot * 74, y, 42, 24))
            count += 1

    # 10 service/maintenance berths near the yard and fuel area.
    for index in range(1, 6):
        positions.append((f"M{index:02d}", 1118, 245 + (index - 1) * 46, 34, 22))
    for index in range(6, 11):
        positions.append((f"M{index:02d}", 1200, 245 + (index - 6) * 46, 34, 22))

    return positions
