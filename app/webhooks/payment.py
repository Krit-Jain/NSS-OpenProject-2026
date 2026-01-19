from fastapi import APIRouter, Depends, HTTPException,Request
from sqlalchemy.orm import Session
from datetime import datetime
import os

from app.database.deps import get_db
from app.donations.models import Donation
from app.webhooks.security import verify_signature

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"]
)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "test-secret")

@router.post("/payment")
async def payment_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    raw_body = await request.body()
    signature = request.headers.get("X-Signature")

    if not signature:
        raise HTTPException(
            status_code=401,
            detail="Missing signature"
        )

    if not verify_signature(raw_body, signature, WEBHOOK_SECRET):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature"
        )

    payload = await request.json()

    donation_id = payload.get("donation_id")
    status = payload.get("status")

    donation = db.query(Donation).filter(
        Donation.id == donation_id
    ).first()

    if not donation:
        raise HTTPException(404, "Donation not found")

    if donation.status != "pending":
        raise HTTPException(400, "Already processed")

    if status not in ["success", "failed"]:
        raise HTTPException(400, "Invalid status")

    donation.status = status
    donation.payment_reference = f"WEBHOOK-{donation_id}"

    db.commit()

    return {
        "donation_id": donation.id,
        "final_status": donation.status
    }

@router.post("/chargeback")
def chargeback_webhook(
    donation_id: int,
    reason: str,
    db: Session = Depends(get_db)
):
    donation = db.query(Donation).filter(
        Donation.id == donation_id
    ).first()

    if not donation:
        raise HTTPException(404, "Donation not found")

    if donation.status != "success":
        raise HTTPException(
            400,
            "Chargeback allowed only on successful donations"
        )

    donation.status = "chargeback"
    donation.refund_reason = reason
    donation.refunded_at = datetime.utcnow()

    db.commit()

    return {
        "donation_id": donation.id,
        "status": donation.status,
        "type": "chargeback"
    }
