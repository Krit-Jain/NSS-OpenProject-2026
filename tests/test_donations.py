import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base
from app.database.deps import get_db

client = TestClient(app)

def test_create_donation(auth_headers):
    res = client.post(
        "/donations",
        json={"amount": 500},
        headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["status"] == "pending"


def test_get_my_donations(auth_headers):
    res = client.get("/donations", headers=auth_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
