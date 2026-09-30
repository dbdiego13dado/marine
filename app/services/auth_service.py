from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.password import hash_password, verify_password
from app.models.marina import Marina
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.schemas.users import UserCreate
from app.services import subscription_service


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower().strip()).first()


def create_user(db: Session, payload: UserCreate | RegisterRequest, role: str | None = None) -> User:
    email = payload.email.lower().strip()
    if get_user_by_email(db, email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    assigned_role = role or getattr(payload, "role", "customer")
    marina_id = payload.marina_id
    if marina_id is None and assigned_role == "customer":
        demo_marina = db.query(Marina).filter(Marina.active.is_(True)).order_by(Marina.id).first()
        marina_id = demo_marina.id if demo_marina else None

    if marina_id is not None and assigned_role in {"marina_admin", "staff"}:
        marina = db.get(Marina, marina_id)
        if marina is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marina not found")
        subscription_service.ensure_staff_limit(db, marina)

    user = User(
        marina_id=marina_id,
        full_name=payload.full_name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        role=assigned_role,
        phone=payload.phone,
        language_preference=payload.language_preference,
        currency_preference=payload.currency_preference,
        is_active=getattr(payload, "is_active", True),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return user
