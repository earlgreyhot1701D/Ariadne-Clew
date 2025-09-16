"""
API endpoint to generate a recap from chat logs using classification and diffing.
"""

from flask import Flask, request, jsonify
from lambda_classifier import classify_blocks
from diffcheck import diff_code_blocks
from schema import validate_recap_output
from pydantic import BaseModel, ValidationError
from typing import Tuple
import logging
import traceback

# App initialization
app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Core processing function
def create_recap_from_log(chat_log: str) -> dict:
    """
    Process chat logs and generate a structured recap.
    """
    if not chat_log or not isinstance(chat_log, str):
        raise ValueError("Invalid or missing 'chat_log' (must be a non-empty string).")

    logger.info("Classifying chat log into blocks.")
    blocks = classify_blocks(chat_log)

    logger.info("Diffing code blocks.")
    recap = diff_code_blocks(blocks)

    logger.info("Validating recap structure.")
    if not validate_recap_output(recap):
        raise RuntimeError("Recap structure validation failed.")

    return recap

# Encapsulated logic for testability
def process_recap_request(data: dict) -> Tuple[dict, int]:
    try:
        logger.debug(f"Received data: {data}")
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

# API route
@app.route('/v1/recap', methods=['POST'])
def generate_recap():
    """
    Classify chat content and produce a structured recap.
    """
    if request.content_type != ContentType.JSON:
        return jsonify({"error": "Content-Type must be application/json"}), HttpStatus.UNSUPPORTED_MEDIA_TYPE

    data = request.get_json(force=True)
    response, status = process_recap_request(data)
    return jsonify(response), status

# Entrypoint
if __name__ == '__main__':
    app.run(debug=True)

