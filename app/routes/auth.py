from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _wants_html(request: Request) -> bool:
    return "text/html" in request.headers.get("accept", "") or "application/x-www-form-urlencoded" in request.headers.get("content-type", "")


async def _request_data(request: Request) -> dict:
    if "application/json" in request.headers.get("content-type", ""):
        return await request.json()
    form = await request.form()
    return dict(form)


def _landing_for_role(role: str) -> str:
    if role in {"super_admin", "marina_admin", "staff"}:
        return "/dashboard"
    return "/ui/bookings"


@router.post("/register", response_model=AuthResponse)
async def register(request: Request, db: Session = Depends(get_db)):
    payload = RegisterRequest(**await _request_data(request))
    user = auth_service.create_user(db, payload, role="customer")
    request.session["user_id"] = user.id
    if _wants_html(request):
        return RedirectResponse(_landing_for_role(user.role), status_code=303)
    return {"message": "User registered", "user": user}


@router.post("/login", response_model=AuthResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    payload = LoginRequest(**await _request_data(request))
    user = auth_service.authenticate_user(db, payload.email, payload.password)
    request.session["user_id"] = user.id
    if _wants_html(request):
        return RedirectResponse(_landing_for_role(user.role), status_code=303)
    return {"message": "Logged in", "user": user}


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    if _wants_html(request):
        return RedirectResponse("/login", status_code=303)
    return JSONResponse({"message": "Logged out"})
