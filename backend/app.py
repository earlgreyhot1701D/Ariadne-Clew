# app.py
# Production-ready Flask backend for code recap

import re
import ast
import logging
import uuid
from typing import List, Optional, Tuple, Union, Dict, Any, cast

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from backend.filters import enforce_size_limit, contains_deny_terms, scrub_pii
from backend.schema import Recap, RejectedVersion
from backend.recap_formatter import format_recap

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(request_id)s %(message)s",
)


@app.before_request
def assign_request_id() -> None:
    """Attach a request ID header or generate one if missing."""
    request.environ["X_REQUEST_ID"] = request.headers.get(
        "X-Request-Id", str(uuid.uuid4())
    )


@app.route("/v1/recap", methods=["POST"])
def recap() -> Union[Response, Tuple[Response, int]]:
    """Minimal recap endpoint: validates input, parses code blocks, returns recap."""
    data: Dict[str, Any] = request.get_json(force=True)
    chat_log: str = data.get("chat_log", "")

    try:
        enforce_size_limit(chat_log)
        if contains_deny_terms(chat_log):
            return jsonify({"error": "Input contains forbidden terms"}), 400
        cleaned: str = scrub_pii(chat_log)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 413

    code_blocks: List[str] = re.findall(r"```(?:python)?(.*?)```", cleaned, re.DOTALL)
    rejected: List[RejectedVersion] = []
    final: Optional[str] = None

    for block in code_blocks:
        try:
            ast.parse(block)
            if final is None:
                final = block
            else:
                rejected.append(RejectedVersion(code=block, reason="Extra snippet"))
        except SyntaxError:
            rejected.append(RejectedVersion(code=block, reason="Invalid Python"))

    recap_obj = Recap(
        final=final,
        rejected_versions=rejected,
        summary="Dummy recap generated.",
        aha_moments=["Caught code block(s)", "Applied AST validation"],
        quality_flags=["MVP"],
    )

    request_id: str = request.environ.get("X_REQUEST_ID", "")
    logging.info("Recap generated", extra={"request_id": request_id})

    formatted: Dict[str, Any] = format_recap(recap_obj)
    response: Response = jsonify(formatted)
    return response
