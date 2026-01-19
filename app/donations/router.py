from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.donations.models import Donation
from app.donations.schemas import DonationCreate, DonationResponse

from app.auth.dependencies import require_admin
from datetime import datetime


router = APIRouter(
    prefix="/donations",
    tags=["Donations"]
)

# Create Donation(Pending)
@router.post("/", response_model=DonationResponse)
def create_donation(
    data: DonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    donation = Donation(
        user_id=current_user.id,
        amount=data.amount,
        status="pending"
    )

    db.add(donation)
    db.commit()
    db.refresh(donation)

    return donation

# Confirm gateway
@router.post("/{donation_id}/confirm")
def confirm_donation_payment(
    donation_id: int,
    success: bool,
    db: Session = Depends(get_db)
):
    donation = db.query(Donation).filter(
        Donation.id == donation_id
    ).first()

    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")

    if donation.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Donation already processed"
        )

    donation.status = "success" if success else "failed"
    donation.payment_reference = f"TXN-{donation_id}"

    db.commit()

    return {
        "donation_id": donation.id,
        "status": donation.status
    }

# Get my Donation
@router.get("/", response_model=list[DonationResponse])
def get_my_donations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Donation)\
        .filter(Donation.user_id == current_user.id)\
        .order_by(Donation.created_at.desc())\
        .all()

@router.post("/{donation_id}/refund")
def refund_donation(
    donation_id: int,
    reason: str,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    donation = db.query(Donation).filter(
        Donation.id == donation_id
    ).first()

    if not donation:
        raise HTTPException(404, "Donation not found")

    if donation.status != "success":
        raise HTTPException(
            400,
            "Only successful donations can be refunded"
        )

    donation.status = "refunded"
    donation.refund_reason = reason
    donation.refunded_at = datetime.utcnow()

    db.commit()

    return {
        "donation_id": donation.id,
        "status": donation.status,
        "refund_reason": donation.refund_reason
    }
