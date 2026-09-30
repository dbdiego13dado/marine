from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import ensure_marina_access, require_roles
from app.database import get_db
from app.models.marina import Marina
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    marina_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("super_admin", "marina_admin", "staff")),
):
    selected_marina_id = marina_id if current_user.role == "super_admin" else current_user.marina_id
    ensure_marina_access(current_user, selected_marina_id)
    marina = db.get(Marina, selected_marina_id)
    if marina is None:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Marina not found")
    return get_dashboard_summary(db, marina)
