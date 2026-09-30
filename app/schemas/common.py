from pydantic import BaseModel, ConfigDict


SUPPORTED_LANGUAGES = {"en", "it"}
SUPPORTED_CURRENCIES = {"EUR", "USD", "GBP"}
USER_ROLES = {"super_admin", "marina_admin", "staff", "customer"}
MARINA_TYPES = {"marina", "yacht_club", "tourist_port", "dry_storage"}
BERTH_STATUSES = {"available", "occupied", "maintenance", "hidden"}
BERTH_CATEGORIES = {"sail", "motor", "catamaran", "other"}
BERTH_USAGE_TYPES = {"transient", "owner", "service"}
BOOKING_STATUSES = {"pending", "confirmed", "cancelled", "completed"}
APPROVAL_STATUSES = {"not_required", "pending_staff", "approved", "rejected"}
PAYMENT_STATUSES = {"unpaid", "paid", "refunded", "failed"}


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
