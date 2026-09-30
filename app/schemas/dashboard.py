from app.schemas.common import ORMModel


class DashboardSummary(ORMModel):
    total_berths: int
    available_berths: int
    occupied_berths: int
    maintenance_berths: int
    pending_bookings: int
    confirmed_bookings: int
    unpaid_bookings: int
    monthly_revenue_mock: float
    currency: str
