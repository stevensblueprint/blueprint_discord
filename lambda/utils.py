from typing import Dict, Any
import os
import base64
import hashlib
import json
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError


def _get_env_variable(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{name}' is not set.")
    return value


def _get_header(headers: Dict[str, Any], name: str):
    if not headers:
        return None
    for k, v in headers.items():
        if k.lower() == name.lower():
            return v
    return None


def derive_key(passphrase: str, salt: bytes) -> bytes:
    key = hashlib.pbkdf2_hmac(
        "sha256", passphrase.encode("utf-8"), salt, 100_000, dklen=32
    )
    return base64.urlsafe_b64encode(key)


def ephemeral_error(msg: str) -> dict:
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"type": 4, "data": {"content": msg, "flags": 64}}),
    }


def _verify(
    public_key_hex: str, signature_hex: str, timestamp: str, raw_body: bytes
) -> bool:
    try:
        verify_key = VerifyKey(bytes.fromhex(public_key_hex))
        message = timestamp.encode("utf-8") + raw_body
        verify_key.verify(message, bytes.fromhex(signature_hex))
        return True
    except (BadSignatureError, ValueError, TypeError):
        return False
