# app/database/init_db.py (recommended)
from app.database.database import Base, engine

# import ALL models here
from app.auth.models import User
from app.users.models import RegistrationDetails
from app.donations.models import Donation

def init_db():
    print(">>> INIT_DB RUNNING <<<")
    print("CREATING TABLES...")
    Base.metadata.create_all(bind=engine)
    print("TABLES CREATED")
