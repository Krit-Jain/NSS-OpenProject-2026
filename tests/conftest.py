import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["WEBHOOK_SECRET"] = "test-secret"

from app.main import app
from app.database.database import Base
from app.database.deps import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def auth_headers():
    client.post("/auth/register", json={
        "email": "user@test.com",
        "password": "password123"
    })

    res = client.post("/auth/login", data={
        "username": "user@test.com",
        "password": "password123"
    })

    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers():
    client.post("/auth/register", json={
        "email": "admin@test.com",
        "password": "password123"
    })

    # manually promote admin (test-only)
    from app.auth.models import User
    db = TestingSessionLocal()
    admin = db.query(User).filter_by(email="admin@test.com").first()
    admin.role = "admin"
    db.commit()

    res = client.post("/auth/login", data={
        "username": "admin@test.com",
        "password": "password123"
    })

    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
