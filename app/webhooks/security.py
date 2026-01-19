import hmac
import hashlib

def verify_signature(
    payload: bytes,
    received_signature: str,
    secret: str
) -> bool:
    computed_signature = hmac.new(
        key=secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        computed_signature,
        received_signature
    )
