import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import inspect, text
from starlette.middleware.sessions import SessionMiddleware

from app.database import Base, SessionLocal, engine
from app.models import *  # noqa: F403 - imports all SQLAlchemy models for metadata creation.
from app.routes import api_routers
from app.routes.pages import router as pages_router
from app.services.seed_service import seed_demo_data


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "app" / "uploads"
STATIC_DIR = BASE_DIR / "app" / "static"


def _ensure_sqlite_schema_updates() -> None:
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    cached_columns: dict[str, set[str]] = {}

    def column_names(table_name: str) -> set[str]:
        if table_name not in table_names:
            return set()
        if table_name not in cached_columns:
            cached_columns[table_name] = {column["name"] for column in inspector.get_columns(table_name)}
        return cached_columns[table_name]

    with engine.begin() as connection:
        def add_column_if_missing(table_name: str, column_name: str, ddl: str) -> None:
            if table_name in table_names and column_name not in column_names(table_name):
                connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {ddl}"))
                cached_columns.setdefault(table_name, set()).add(column_name)

        settings_columns = column_names("marina_settings")
        if "marina_settings" in table_names and "rules_pdf_url" not in settings_columns:
            connection.execute(text("ALTER TABLE marina_settings ADD COLUMN rules_pdf_url VARCHAR(255)"))
        add_column_if_missing("marina_settings", "nautical_access_notes", "nautical_access_notes TEXT")
        add_column_if_missing("marina_settings", "seabed_notes", "seabed_notes TEXT")
        add_column_if_missing("marina_settings", "accepts_catamarans", "accepts_catamarans BOOLEAN NOT NULL DEFAULT 1")
        add_column_if_missing("marina_settings", "accepts_multihulls", "accepts_multihulls BOOLEAN NOT NULL DEFAULT 1")

        add_column_if_missing("marinas", "structure_type", "structure_type VARCHAR(40) NOT NULL DEFAULT 'marina'")
        add_column_if_missing("marinas", "public_slug", "public_slug VARCHAR(140)")
        add_column_if_missing("marinas", "short_description", "short_description VARCHAR(255)")
        add_column_if_missing("marinas", "long_description", "long_description TEXT")
        add_column_if_missing("marinas", "latitude", "latitude FLOAT")
        add_column_if_missing("marinas", "longitude", "longitude FLOAT")

        berth_columns = column_names("berth_slots")
        if "berth_slots" in table_names and "usage_type" not in berth_columns:
            connection.execute(text("ALTER TABLE berth_slots ADD COLUMN usage_type VARCHAR(40) NOT NULL DEFAULT 'transient'"))
        add_column_if_missing("berth_slots", "zone_id", "zone_id INTEGER")
        add_column_if_missing("berth_slots", "special_approval_required", "special_approval_required BOOLEAN NOT NULL DEFAULT 0")

        add_column_if_missing("bookings", "extra_services_total", "extra_services_total NUMERIC(10,2) NOT NULL DEFAULT 0")
        add_column_if_missing("bookings", "approval_status", "approval_status VARCHAR(40) NOT NULL DEFAULT 'not_required'")
        add_column_if_missing("bookings", "arrival_time", "arrival_time VARCHAR(20)")
        add_column_if_missing("bookings", "departure_time", "departure_time VARCHAR(20)")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    _ensure_sqlite_schema_updates()
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="MarinaSuite SaaS MVP",
    description="Multi-tenant SaaS MVP for marinas, docks, and small tourist ports.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "change-this-secret-before-production"),
    same_site="lax",
    https_only=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def no_store_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

for router in api_routers:
    app.include_router(router)

app.include_router(pages_router)


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "product": "MarinaSuite SaaS MVP"}


@app.get("/service-worker.js", include_in_schema=False)
def service_worker_cleanup():
    content = """
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.map((key) => caches.delete(key))))
      .then(() => self.registration.unregister())
      .then(() => self.clients.claim())
  );
});
"""
    return Response(content=content, media_type="application/javascript")
