from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from app.models.berth import BerthSlot
from app.models.extra_service import ExtraService
from app.models.seasonal_rate import SeasonalRate


def _date_in_rate_window(current_day: date, rate: SeasonalRate) -> bool:
    start_key = (rate.start_month, rate.start_day)
    end_key = (rate.end_month, rate.end_day)
    current_key = (current_day.month, current_day.day)
    if start_key <= end_key:
        return start_key <= current_key <= end_key
    return current_key >= start_key or current_key <= end_key


def _seasonal_multiplier(db, berth: BerthSlot, start_date: date, end_date: date) -> tuple[Decimal, Decimal, Decimal]:
    if db is None:
        return (Decimal("1"), Decimal("1"), Decimal("1"))
    rates = (
        db.query(SeasonalRate)
        .filter(SeasonalRate.marina_id == berth.marina_id, SeasonalRate.active.is_(True))
        .order_by(SeasonalRate.zone_id.is_(None), SeasonalRate.berth_category.is_(None))
        .all()
    )
    if not rates:
        return (Decimal("1"), Decimal("1"), Decimal("1"))
    for rate in rates:
        if rate.zone_id and berth.zone_id != rate.zone_id:
            continue
        if rate.berth_category and berth.category != rate.berth_category:
            continue
        current_day = start_date
        while current_day < end_date:
            if _date_in_rate_window(current_day, rate):
                return (
                    Decimal(str(rate.day_multiplier)),
                    Decimal(str(rate.week_multiplier)),
                    Decimal(str(rate.month_multiplier)),
                )
            current_day = date.fromordinal(current_day.toordinal() + 1)
    return (Decimal("1"), Decimal("1"), Decimal("1"))


def calculate_booking_price(berth: BerthSlot, start_date: date, end_date: date, db=None) -> Decimal:
    days = (end_date - start_date).days
    month_blocks, remainder = divmod(days, 30)
    week_blocks, day_blocks = divmod(remainder, 7)
    day_multiplier, week_multiplier, month_multiplier = _seasonal_multiplier(db, berth, start_date, end_date)
    total = (
        Decimal(month_blocks) * Decimal(str(berth.price_per_month)) * month_multiplier
        + Decimal(week_blocks) * Decimal(str(berth.price_per_week)) * week_multiplier
        + Decimal(day_blocks) * Decimal(str(berth.price_per_day)) * day_multiplier
    )
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_extra_service_total(service: ExtraService, quantity: int, days: int) -> Decimal:
    units = quantity if service.billing_mode == "per_booking" else quantity * max(days, 1)
    total = Decimal(units) * Decimal(str(service.amount))
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
