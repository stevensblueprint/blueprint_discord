import logging
import os
import uuid
import json
import base64
import time
from typing import Dict, Any

import boto3
import requests
from cryptography.fernet import Fernet, InvalidToken

from utils import _get_header, _verify, _get_env_variable, derive_key, ephemeral_error

logger = logging.getLogger()
logger.setLevel(logging.INFO)

PUBLIC_KEY = _get_env_variable("DISCORD_PUBLIC_KEY")
SUMMARY_BUCKET_NAME = _get_env_variable("SUMMARY_BUCKET_NAME")

s3 = boto3.client("s3")


def handle_env_store(interaction: Dict[str, Any]) -> Dict[str, Any]:
    options = {opt["name"]: opt["value"] for opt in interaction["data"]["options"][0]["options"]}
    passphrase = options["passphrase"]
    file_id = options["file"]

    attachments = interaction["data"]["resolved"]["attachments"]
    url = attachments[file_id]["url"]

    response = requests.get(url, timeout=15)
    if not response.ok:
        return ephemeral_error("Failed to download the attachment.")

    content = response.content
    salt = os.urandom(16)
    key = derive_key(passphrase, salt)
    encrypted = Fernet(key).encrypt(content)

    storage_key = str(uuid.uuid4())
    s3.put_object(
        Bucket=SUMMARY_BUCKET_NAME,
        Key=f"envfiles/{storage_key}",
        Body=salt + encrypted,
        Metadata={"uploaded-at": str(int(time.time()))},
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "type": 4,
            "data": {
                "content": f"File stored. Your key: `{storage_key}`",
                "flags": 64,
            },
        }),
    }


def handle_env_get(interaction: Dict[str, Any]) -> Dict[str, Any]:
    options = {opt["name"]: opt["value"] for opt in interaction["data"]["options"][0]["options"]}
    name = options["name"]
    passphrase = options["passphrase"]

    try:
        obj = s3.get_object(Bucket=SUMMARY_BUCKET_NAME, Key=f"envfiles/{name}")
    except s3.exceptions.NoSuchKey:
        return ephemeral_error("File not found.")
    except Exception:
        return ephemeral_error("File not found.")

    uploaded_at = int(obj.get("Metadata", {}).get("uploaded-at", 0))
    if time.time() - uploaded_at > 86400:
        return ephemeral_error("This key has expired. Keys are valid for 24 hours.")

    data = obj["Body"].read()
    salt = data[:16]
    blob = data[16:]

    key = derive_key(passphrase, salt)
    try:
        decrypted = Fernet(key).decrypt(blob).decode("utf-8")
    except (InvalidToken, Exception):
        return ephemeral_error("Invalid passphrase or corrupted file.")

    if len(decrypted) > 1900:
        decrypted = decrypted[:1900] + "\n... (truncated)"

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "type": 4,
            "data": {
                "content": f"```\n{decrypted}\n```",
                "flags": 64,
            },
        }),
    }

def handle_designer() -> Dict[str, Any]:
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "type": 4,
            "data": {
                "content": "Designer command is under construction. Stay tuned!",
                "flags": 64,
            },
        }),
    }

def handler(event: Dict[str, Any], ctx: Any) -> Dict[str, Any]:
    headers = event.get("headers")
    if not headers:
        return {"statusCode": 400, "body": "Missing headers."}
    sig = _get_header(headers, "x-signature-ed25519")
    ts = _get_header(headers, "x-signature-timestamp")

    if not sig or not ts:
        return {"statusCode": 400, "body": "Missing signature headers."}

    raw_body = event.get("body", "").encode("utf-8")
    if event.get("isBase64Encoded", False):
        raw_body = base64.b64decode(raw_body)

    if not _verify(PUBLIC_KEY, sig, ts, raw_body):
        return {"statusCode": 401, "body": "Invalid request signature."}

    interaction = json.loads(raw_body.decode("utf-8"))

    # Discord ping (type 1) — required for endpoint verification
    if interaction.get("type") == 1:
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"type": 1}),
        }

    # Slash command (type 2)
    if interaction.get("type") == 2:
        name = (interaction.get("data") or {}).get("name")

        if name == "env":
            subcommand = interaction["data"]["options"][0]["name"]
            if subcommand == "store":
                return handle_env_store(interaction)
            if subcommand == "get":
                return handle_env_get(interaction)
            
        if name == "designer":
            return handle_designer()
            

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"type": 4, "data": {"content": f"Unknown command: {name}"}}
            ),
        }

    return {"statusCode": 200, "body": ""}
