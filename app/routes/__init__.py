from . import auth, berths, boats, bookings, dashboard, maps, marinas, payments, plans, users

api_routers = [
    auth.router,
    users.router,
    marinas.router,
    plans.router,
    berths.router,
    boats.router,
    bookings.router,
    payments.router,
    maps.router,
    dashboard.router,
]

__all__ = ["api_routers"]
