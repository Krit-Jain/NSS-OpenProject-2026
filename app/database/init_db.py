# app/database/init_db.py (recommended)
from app.database.database import Base, engine

# import ALL models here
from app.auth.models import User
from app.users.models import RegistrationDetails

def init_db():
    Base.metadata.create_all(bind=engine)
