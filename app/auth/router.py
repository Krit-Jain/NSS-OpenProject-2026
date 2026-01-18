# Registration API
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app.auth import schemas, models, utils

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
def register_user(user: schemas.UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = utils.hash_password(user.password)

    new_user = models.User(
        email=user.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}

# Login API
@router.post("/login", response_model=schemas.TokenResponse)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not utils.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = utils.create_access_token(
        data={"sub": db_user.email, "role": db_user.role}
    )

    return {"access_token": token}
