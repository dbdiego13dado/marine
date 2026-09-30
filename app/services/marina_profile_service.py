from sqlalchemy.orm import Session, joinedload

from app.models.extra_service import ExtraService
from app.models.marina import Marina
from app.models.marina_map import BerthPosition, MarinaMap
from app.models.marina_photo import MarinaPhoto
from app.models.marina_service import MarinaService
from app.models.marina_settings import MarinaSettings
from app.models.marina_zone import MarinaZone
from app.models.seasonal_rate import SeasonalRate


def list_public_marinas(db: Session) -> list[Marina]:
    return (
        db.query(Marina)
        .filter(Marina.active.is_(True))
        .order_by(Marina.country, Marina.city, Marina.name)
        .all()
    )


def get_public_profile(db: Session, marina_id: int) -> Marina | None:
    return (
        db.query(Marina)
        .options(
            joinedload(Marina.settings),
            joinedload(Marina.services),
            joinedload(Marina.photos),
            joinedload(Marina.zones),
            joinedload(Marina.extra_services),
            joinedload(Marina.maps).joinedload(MarinaMap.berth_positions).joinedload(BerthPosition.berth_slot),
        )
        .filter(Marina.id == marina_id, Marina.active.is_(True))
        .first()
    )


def list_visible_services(db: Session, marina_id: int) -> list[MarinaService]:
    return (
        db.query(MarinaService)
        .filter(
            MarinaService.marina_id == marina_id,
            MarinaService.active.is_(True),
            MarinaService.customer_visible.is_(True),
        )
        .order_by(MarinaService.category, MarinaService.name)
        .all()
    )


def list_visible_photos(db: Session, marina_id: int) -> list[MarinaPhoto]:
    return (
        db.query(MarinaPhoto)
        .filter(MarinaPhoto.marina_id == marina_id, MarinaPhoto.active.is_(True))
        .order_by(MarinaPhoto.sort_order, MarinaPhoto.id)
        .all()
    )


def list_visible_zones(db: Session, marina_id: int) -> list[MarinaZone]:
    return (
        db.query(MarinaZone)
        .filter(MarinaZone.marina_id == marina_id, MarinaZone.customer_visible.is_(True))
        .order_by(MarinaZone.sort_order, MarinaZone.name)
        .all()
    )


def list_bookable_extra_services(db: Session, marina_id: int) -> list[ExtraService]:
    return (
        db.query(ExtraService)
        .filter(
            ExtraService.marina_id == marina_id,
            ExtraService.active.is_(True),
            ExtraService.customer_visible.is_(True),
        )
        .order_by(ExtraService.name)
        .all()
    )


def list_seasonal_rates(db: Session, marina_id: int) -> list[SeasonalRate]:
    return (
        db.query(SeasonalRate)
        .filter(SeasonalRate.marina_id == marina_id, SeasonalRate.active.is_(True))
        .order_by(SeasonalRate.start_month, SeasonalRate.start_day, SeasonalRate.name)
        .all()
    )


def get_or_create_settings(db: Session, marina: Marina) -> MarinaSettings:
    settings = db.query(MarinaSettings).filter(MarinaSettings.marina_id == marina.id).first()
    if settings is None:
        settings = MarinaSettings(marina_id=marina.id)
        db.add(settings)
        db.flush()
    return settings
