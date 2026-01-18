# Creating a protected root at user level
from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.auth.models import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def read_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at
    }

# Registration Routes
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.users import models, schemas

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/registration", response_model=schemas.RegistrationResponse)
def create_registration(
    data: schemas.RegistrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = (
        db.query(models.RegistrationDetails)
        .filter(models.RegistrationDetails.user_id == current_user.id)
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Registration already exists")

    registration = models.RegistrationDetails(
        user_id=current_user.id,
        **data.dict()
    )

    db.add(registration)
    db.commit()
    db.refresh(registration)

    return registration

@router.get("/registration", response_model=schemas.RegistrationResponse)
def get_my_registration(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    registration = (
        db.query(models.RegistrationDetails)
        .filter(models.RegistrationDetails.user_id == current_user.id)
        .first()
    )

    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    return registration

