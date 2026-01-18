from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.donations.models import Donation
from app.donations.schemas import DonationCreate, DonationResponse

router = APIRouter(
    prefix="/donations",
    tags=["Donations"]
)

# Create Donation
@router.post("/", response_model=DonationResponse)
def create_donation(
    data: DonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    donation = Donation(
        user_id=current_user.id,
        amount=data.amount,
        status="PENDING"
    )

    db.add(donation)
    db.commit()
    db.refresh(donation)

    return donation

# Mark donation as success
@router.post("/{donation_id}/success")
def mark_donation_success(
    donation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    donation = db.query(Donation).filter(
        Donation.id == donation_id,
        Donation.user_id == current_user.id
    ).first()

    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")

    donation.status = "SUCCESS"
    donation.payment_reference = f"PAY-{donation_id}"

    db.commit()

    return {"message": "Donation successful"}

# Mark Donation as FAILED
@router.post("/{donation_id}/failed")
def mark_donation_failed(
    donation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    donation = db.query(Donation).filter(
        Donation.id == donation_id,
        Donation.user_id == current_user.id
    ).first()

    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")

    donation.status = "FAILED"
    db.commit()

    return {"message": "Donation failed"}

# Get my donations
@router.get("/", response_model=list[DonationResponse])
def get_my_donations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Donation)\
        .filter(Donation.user_id == current_user.id)\
        .all()

