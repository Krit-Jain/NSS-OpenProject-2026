from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database.database import Base


class Donation(Base):
    __tablename__ = "donations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    amount = Column(Float, nullable=False)

    status = Column(
        String,
        default="PENDING"  # PENDING | SUCCESS | FAILED
    )

    payment_reference = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

refund_reason = Column(String, nullable=True)
refunded_at = Column(DateTime, nullable=True)