"""
API endpoint to generate a recap from chat logs using filters, classifier (Bedrock),
code handler, diffing, recap formatter, and memory handler.
"""

from __future__ import annotations

import json
import logging
import os
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import boto3
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from pydantic import BaseModel, ValidationError

# ✅ Use the richer root-level handlers, not backend stubs
from code_handler import validate_snippet, extract_code_blocks, version_snippets, reconcile_intent, summarize_session
from diffcheck import diff_code_blocks
from backend.filters import enforce_size_limit, contains_deny_terms, scrub_pii
from backend.recap_formatter import format_recap
from backend.memory_handler import store_recap
from backend.schema import Recap

# Load environment variables
load_dotenv()

# App initialization
app = Flask(__name__)
CORS(app)

# Logging setup (ENV-controlled)
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "WARNING"))
logger = logging.getLogger(__name__)

# AWS Bedrock client
try:
    bedrock = boto3.client(
        "bedrock-runtime", region_name=os.environ.get("AWS_REGION", "us-east-1")
    )
except Exception as e:
    logger.warning("Bedrock client could not be initialized: %s", e)
    bedrock = None


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


PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def load_prompts() -> str:
    """Load system and classifier prompts from the prompts/ directory."""
    try:
        system_preamble = (PROMPTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
        classifier_instructions = (PROMPTS_DIR / "classifier_prompt.md").read_text(
            encoding="utf-8"
        )
        return f"{system_preamble}\n\n{classifier_instructions}"
    except FileNotFoundError as e:
        logger.critical(f"Prompt file missing: {e}")
        raise RuntimeError(f"Required prompt file not found: {PROMPTS_DIR}") from e


def classify_with_bedrock(prompt: str) -> List[Dict[str, Any]]:
    """Call Bedrock Claude model to classify chat log into blocks."""
    if bedrock is None:
        logger.warning("Bedrock not initialized; returning raw text block.")
        return [{"type": "text", "content": prompt}]

    model_id = os.environ.get(
        "BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0"
    )

    body = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000,
        "anthropic_version": "bedrock-2023-05-31",
    }

    try:
        resp = bedrock.invoke_model(
            modelId=model_id,
            accept="application/json",
            contentType="application/json",
            body=json.dumps(body),
        )
        payload: Any = json.loads(resp["body"].read().decode("utf-8"))

        # TODO: Implement structured parsing instead of always text
        if isinstance(payload, dict) and "content" in payload:
            content_list = payload["content"]
            if isinstance(content_list, list) and len(content_list) > 0:
                response_text = content_list[0].get("text", "")
                return [{"content": response_text, "type": "text"}]

        logger.warning("Unexpected Bedrock response format")
        return []
    except Exception as e:
        logger.error(f"Bedrock classification failed: {e}")
        raise RuntimeError("Classification step failed.") from e


def create_recap_from_log(chat_log: str) -> Dict[str, Any]:
    """Process chat logs and generate a structured recap payload (JSON-serializable dict)."""
    if not chat_log or not isinstance(chat_log, str):
        raise ValueError("Invalid or missing 'chat_log' (must be a non-empty string).")

    enforce_size_limit(chat_log)
    if contains_deny_terms(chat_log):
        raise ValueError("Input contains unsafe terms.")
    chat_log = scrub_pii(chat_log)

    full_prompt = f"{load_prompts()}\n\n{chat_log}"
    blocks = classify_with_bedrock(full_prompt)

    validated_blocks: List[Dict[str, Any]] = []
    for block in blocks:
        content = block.get("content", "")
        if block.get("type") == "code":
            result = validate_snippet(content)
            block["validation"] = result
        validated_blocks.append(block)

    recap_dict: Dict[str, Any] = diff_code_blocks(validated_blocks)

    recap_model: Recap = Recap.model_validate(recap_dict)
    recap_payload: Dict[str, Any] = format_recap(recap_model)

    store_recap("last_recap", recap_payload)

    return recap_payload


def process_recap_request(data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Encapsulate request handling to keep the route thin and testable."""
    try:
        parsed = RecapRequest(**data)
        recap = create_recap_from_log(parsed.chat_log)
        return recap, HttpStatus.OK

    except ValidationError as ve:
        logger.warning(f"Validation error: {ve}")
        return {"error": "Invalid request format or missing fields."}, HttpStatus.BAD_REQUEST
    except ValueError as ve:
        logger.warning(f"Value error: {ve}")
        return {"error": str(ve)}, HttpStatus.BAD_REQUEST
    except RuntimeError as re:
        logger.error(f"Runtime error: {re}")
        return {"error": str(re)}, HttpStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        logger.critical(f"Unhandled error: {e}\n{traceback.format_exc()}")
        return {"error": "Internal server error."}, HttpStatus.INTERNAL_SERVER_ERROR


@app.route("/v1/recap", methods=["POST"])
def generate_recap() -> Union[Response, Tuple[Response, int]]:
    """Classify chat content and produce a structured recap."""
    if request.content_type != ContentType.JSON:
        return jsonify({"error": "Content-Type must be application/json"}), HttpStatus.UNSUPPORTED_MEDIA_TYPE

    data: Dict[str, Any] = request.get_json(force=True)
    response, status = process_recap_request(data)
    return jsonify(response), status


if __name__ == "__main__":
    app.run(debug=True)
