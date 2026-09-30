from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import ensure_marina_access, get_current_user, require_roles
from app.database import get_db
from app.models.user import User
from app.schemas.users import UserCreate, UserRead
from app.services import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "marina_admin", "staff")),
):
    query = db.query(User)
    if current_user.role in {"marina_admin", "staff"}:
        query = query.filter(User.marina_id == current_user.marina_id)
    return query.order_by(User.created_at.desc()).all()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "marina_admin")),
):
    if current_user.role == "marina_admin":
        ensure_marina_access(current_user, payload.marina_id)
        if payload.role not in {"staff", "customer"}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Marina admins can create staff or customers")
    return auth_service.create_user(db, payload)
