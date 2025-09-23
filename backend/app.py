import re
import ast
import logging
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from filters import enforce_size_limit, contains_deny_terms, scrub_pii
from schema import Recap, RejectedVersion
from recap_formatter import format_recap

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(request_id)s %(message)s"
)


@app.before_request
def assign_request_id():
    # Prefer client-provided X-Request-Id header; fall back to generated UUID
    request.environ["X_REQUEST_ID"] = request.headers.get(
        "X-Request-Id", str(uuid.uuid4())
    )


@app.route("/v1/recap", methods=["POST"])
def recap():
    data = request.get_json(force=True)
    chat_log = data.get("chat_log", "")

    try:
        enforce_size_limit(chat_log)
        if contains_deny_terms(chat_log):
            return jsonify({"error": "Input contains forbidden terms"}), 400
        cleaned = scrub_pii(chat_log)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 413

    # Dummy classifier pipeline
    code_blocks = re.findall(r"```(?:python)?(.*?)```", cleaned, re.DOTALL)
    rejected = []
    final = None
    if code_blocks:
        for block in code_blocks:
            try:
                ast.parse(block)
                if not final:
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

    request_id = request.environ.get("X_REQUEST_ID", "")
    logging.info("Recap generated", extra={"request_id": request_id})
    return jsonify(format_recap(recap_obj))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
