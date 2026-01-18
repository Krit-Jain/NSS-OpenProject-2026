from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DonationCreate(BaseModel):
    amount: float


class DonationResponse(BaseModel):
    id: int
    amount: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
