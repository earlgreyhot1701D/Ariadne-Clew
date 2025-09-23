"""
API endpoint to generate a recap from chat logs using filters, classifier (Bedrock),
code handler, diffing, recap formatter, and memory handler.
"""

from flask import Flask, request, jsonify
from pathlib import Path
import logging
import traceback
import boto3
import os
import json

from diffcheck import diff_code_blocks
from schema import validate_recap_output
from filters import enforce_size_limit, contains_deny_terms, scrub_pii
from code_handler import validate_code_snippet
from recap_formatter import format_recap_outputs
from memory_handler import store_recap

from pydantic import BaseModel, ValidationError
from typing import Tuple

# App initialization
app = Flask(__name__)

# Logging setup (ENV-controlled)
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "WARNING"))
logger = logging.getLogger(__name__)

# AWS Bedrock client (TODO: add timeouts/retries for prod)
bedrock = boto3.client(
    "bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1")
)


# Constants
class ContentType:
    JSON = "application/json"


class HttpStatus:
    OK = 200
    BAD_REQUEST = 400
    UNSUPPORTED_MEDIA_TYPE = 415
    INTERNAL_SERVER_ERROR = 500


# Request schema
class RecapRequest(BaseModel):
    chat_log: str


def load_prompts() -> str:
    """Load system and classifier prompts from repo root."""
    try:
        system_preamble = Path("system_prompt.md").read_text()
        classifier_instructions = Path("classifier_prompt.md").read_text()
        return f"{system_preamble}\n\n{classifier_instructions}"
    except FileNotFoundError as e:
        logger.critical(f"Prompt file missing: {e}")
        raise RuntimeError("Required prompt file not found.")


def classify_with_bedrock(prompt: str) -> list:
    """Call Bedrock model to classify chat log into blocks."""
    model_id = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-v2")
    body = {"inputText": prompt}
    try:
        resp = bedrock.invoke_model(
            modelId=model_id,
            accept="application/json",
            contentType="application/json",
            body=json.dumps(body),
        )
        payload = json.loads(resp["body"].read().decode("utf-8"))
        return payload.get("blocks", [])
    except Exception as e:
        logger.error(f"Bedrock classification failed: {e}")
        raise RuntimeError("Classification step failed.")


# Core processing function
def create_recap_from_log(chat_log: str) -> dict:
    """Process chat logs and generate a structured recap."""
    if not chat_log or not isinstance(chat_log, str):
        raise ValueError("Invalid or missing 'chat_log' (must be a non-empty string).")

    logger.debug(f"Chat log length: {len(chat_log)}")

    # Apply filters
    enforce_size_limit(chat_log)
    if contains_deny_terms(chat_log):
        raise ValueError("Input contains unsafe terms.")
    chat_log = scrub_pii(chat_log)

    # Build prompt
    full_prompt = f"{load_prompts()}\n\n{chat_log}"
    logger.debug(f"Prompt length after merging: {len(full_prompt)}")

    # Classification (via Bedrock)
    logger.debug("Classifying chat log into blocks.")
    blocks = classify_with_bedrock(full_prompt)

    # Validate code snippets
    validated_blocks = []
    for block in blocks:
        content = block.get("content", "")
        result = validate_code_snippet(content)
        block["validation"] = result
        validated_blocks.append(block)

    # Diffing
    logger.debug("Reconciling code blocks.")
    recap = diff_code_blocks(validated_blocks)

    # Format recap (JSON + human-readable)
    recap = format_recap_outputs(recap)
    logger.debug(f"Final recap keys: {list(recap.keys())}")

    # Schema validation
    logger.debug("Validating recap structure.")
    if not validate_recap_output(recap):
        raise RuntimeError("Recap structure validation failed.")

    # Memory store
    store_recap(recap)

    return recap


# Encapsulated logic for testability
def process_recap_request(data: dict) -> Tuple[dict, int]:
    try:
        parsed = RecapRequest(**data)
        recap = create_recap_from_log(parsed.chat_log)
        return recap, HttpStatus.OK

    except ValidationError as ve:
        logger.warning(f"Validation error: {ve}")
        return {
            "error": "Invalid request format or missing fields."
        }, HttpStatus.BAD_REQUEST

    except ValueError as ve:
        logger.warning(f"Value error: {ve}")
        return {"error": str(ve)}, HttpStatus.BAD_REQUEST

    except RuntimeError as re:
        logger.error(f"Runtime error: {re}")
        return {"error": str(re)}, HttpStatus.INTERNAL_SERVER_ERROR

    except Exception as e:
        logger.critical(f"Unhandled error: {e}\n{traceback.format_exc()}")
        return {"error": "Internal server error."}, HttpStatus.INTERNAL_SERVER_ERROR


# API route
@app.route("/v1/recap", methods=["POST"])
def generate_recap():
    """Classify chat content and produce a structured recap."""
    if request.content_type != ContentType.JSON:
        return (
            jsonify({"error": "Content-Type must be application/json"}),
            HttpStatus.UNSUPPORTED_MEDIA_TYPE,
        )

    data = request.get_json(force=True)
    response, status = process_recap_request(data)
    return jsonify(response), status


# Entrypoint
if __name__ == "__main__":
    app.run(debug=True)
