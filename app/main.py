from fastapi import FastAPI

app = FastAPI(
    title="NGO Registration and Donation Management System",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"status": "Server running successfully"}

# Connecting router
from app.auth.router import router as auth_router

app.include_router(auth_router)

# Creating Tables(Temporary)
from app.database.database import engine
from app.database.base import Base
from app.auth.models import User

Base.metadata.create_all(bind=engine)

# Registering the router(User level)
from app.users.router import router as user_router

app.include_router(user_router)

# Registering admin router
from app.admin.router import router as admin_router

app.include_router(admin_router)

