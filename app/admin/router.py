from fastapi import APIRouter, Depends
from app.auth.dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def admin_dashboard(admin_user = Depends(require_admin)):
    return {
        "message": "Welcome Admin",
        "admin_email": admin_user.email
    }
