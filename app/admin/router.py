from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import csv
from fastapi.responses import StreamingResponse
from io import StringIO

from app.database.database import get_db
from app.auth.dependencies import require_admin
from app.donations.models import Donation
from app.users.models import RegistrationDetails

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def admin_dashboard(admin_user = Depends(require_admin)):
    return {
        "message": "Welcome Admin",
        "admin_email": admin_user.email
    }

@router.get("/analytics/summary")
def donation_summary(
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    total_amount = db.query(
        func.coalesce(func.sum(Donation.amount), 0)
    ).filter(Donation.status == "success").scalar()

    total_count = db.query(Donation).count()

    success_count = db.query(Donation).filter(
        Donation.status == "success"
    ).count()

    failed_count = db.query(Donation).filter(
        Donation.status == "failed"
    ).count()

    pending_count = db.query(Donation).filter(
        Donation.status == "pending"
    ).count()

    return {
        "total_amount": total_amount,
        "total_donations": total_count,
        "success": success_count,
        "failed": failed_count,
        "pending": pending_count
    }

@router.get("/donations")
def list_donations(
    status: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    query = db.query(Donation)

    if status:
        query = query.filter(Donation.status == status)

    if start_date:
        query = query.filter(Donation.created_at >= start_date)

    if end_date:
        query = query.filter(Donation.created_at <= end_date)

    donations = query.order_by(Donation.created_at.desc()).all()
    return donations

@router.get("/analytics/daily")
def daily_donations(
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    results = (
        db.query(
            func.date(Donation.created_at).label("date"),
            func.sum(Donation.amount).label("total")
        )
        .filter(Donation.status == "success")
        .group_by(func.date(Donation.created_at))
        .order_by(func.date(Donation.created_at))
        .all()
    )

    return [
        {"date": r.date, "total_amount": r.total}
        for r in results
    ]

@router.get("/analytics/top-ngos")
def top_ngos(
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    results = (
        db.query(
            Donation.ngo_id,
            func.sum(Donation.amount).label("total")
        )
        .filter(Donation.status == "success")
        .group_by(Donation.ngo_id)
        .order_by(func.sum(Donation.amount).desc())
        .limit(5)
        .all()
    )

    return results

# Total registrations count
@router.get("/registrations/count")
def get_total_registrations(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    total = db.query(func.count(RegistrationDetails.id)).scalar()
    return {"total_registrations": total}

# Filter Registrations
@router.get("/registrations")
def list_registrations(
    city: str | None = Query(None),
    state: str | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    query = db.query(RegistrationDetails)

    if city:
        query = query.filter(RegistrationDetails.city == city)

    if state:
        query = query.filter(RegistrationDetails.state == state)

    if start_date:
        query = query.filter(RegistrationDetails.created_at >= start_date)

    if end_date:
        query = query.filter(RegistrationDetails.created_at <= end_date)

    return query.order_by(RegistrationDetails.created_at.desc()).all()

# Export Registration Data
@router.get("/registrations/export")
def export_registrations(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    registrations = db.query(RegistrationDetails).all()

    output = StringIO()
    writer = csv.writer(output)

    # CSV Header
    writer.writerow([
        "id", "user_id", "full_name", "phone",
        "address", "city", "state", "created_at"
    ])

    for r in registrations:
        writer.writerow([
            r.id, r.user_id, r.full_name, r.phone,
            r.address, r.city, r.state, r.created_at
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=registrations.csv"
        }
    )