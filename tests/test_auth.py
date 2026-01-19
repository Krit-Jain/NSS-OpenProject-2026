import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base
from app.database.deps import get_db

client = TestClient(app)

def test_user_registration():
    res = client.post("/auth/register", json={
        "email": "new@test.com",
        "password": "password123"
    })
    assert res.status_code == 201


def test_login_success():
    client.post("/auth/register", json={
        "email": "user@test.com",
        "password": "password123"
    })

    res = client.post("/auth/login", data={
        "username": "user@test.com",
        "password": "password123"
    })

    assert res.status_code == 200
