from pydantic import BaseModel
from typing import Optional

class RegistrationCreate(BaseModel):
    full_name: str
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None

class RegistrationResponse(BaseModel):
    full_name: str
    phone: str
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]

    class Config:
        orm_mode = True
