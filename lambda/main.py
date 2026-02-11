import logging
from parser import GranolarParser
from typing import Dict, Any
from utils import _get_header, _verify, _get_env_variable
import base64
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

PUBLIC_KEY = _get_env_variable("DISCORD_PUBLIC_KEY")


def main(event: Dict[str, Any], ctx: Any) -> Dict[str, Any]:
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
    if interaction.get("type") == 1:
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"type": 1}),
        }

    source = "https://example.com/granolar-article"
    parser = GranolarParser(source)

    try:
        html_text = parser.read_html()
        script_text = parser.extract_second_to_last_script(html_text)
        html_payload = parser.decode_payload(script_text)
        markdown_content = parser.html_to_markdown(html_payload)
    except Exception as e:
        logging.error(f"Error processing the source: {e}")
        return {"statusCode": 500, "body": str(e)}

    if interaction.get("type") == 2:
        name = (interaction.get("data") or {}).get("name")

        if name == "ping":
            return {
                "statusCode": 200,
                "headers": {"content-type": "application/json"},
                "body": json.dumps({"type": 4, "data": {"content": markdown_content}}),
            }

        return {
            "statusCode": 200,
            "headers": {"content-type": "application/json"},
            "body": json.dumps(
                {"type": 4, "data": {"content": f"Unknown command: {name}"}}
            ),
        }

    return {"statusCode": 200, "body": ""}


if __name__ == "__main__":
    result = main({}, {})
