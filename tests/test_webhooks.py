import hmac, hashlib, json
import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.main import app
from app.database.database import Base
from app.database.deps import get_db

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "test-secret")

client = TestClient(app)
def generate_signature(raw_body: bytes) -> str:
    return hmac.new(
        WEBHOOK_SECRET.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()



def test_webhook_success():
    payload = {"donation_id": 1, "status": "success"}

    raw_body = json.dumps(payload, separators=(",", ":")).encode()
    signature = generate_signature(raw_body)

    res = client.post(
        "/webhooks/payment",
        content=raw_body,
        headers={
            "X-Signature": signature,
            "Content-Type": "application/json"
        }
    )

    assert res.status_code == 200


def test_webhook_invalid_signature():
    res = client.post(
        "/webhooks/payment",
        json={"donation_id": 1, "status": "failed"},
        headers={"X-Signature": "invalid"}
    )

    assert res.status_code == 401
