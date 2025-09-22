from flask import Flask, request, jsonify
from flask_cors import CORS
from filters import enforce_size_limit, contains_deny_terms, scrub_pii

app = Flask(__name__)
CORS(app)

@app.route("/recap", methods=["POST"])
def recap():
    if not request.is_json:
        return jsonify({"error": "Expected JSON body"}), 400

    data = request.get_json(force=True)
    chat_log = data.get("chat_log")

    if not isinstance(chat_log, str):
        return jsonify({"error": "'chat_log' must be a string"}), 400

    try:
        enforce_size_limit(chat_log)
        if contains_deny_terms(chat_log):
            return jsonify({"error": "Input contains forbidden terms"}), 400

        cleaned = scrub_pii(chat_log)

        # TODO: Replace this with real recap engine
        human = f"Recap of your transcript. Length: {len(cleaned)} characters."
        raw = {
            "summary": "This is a placeholder summary.",
            "status": "ok",
            "length": len(cleaned),
        }
        return jsonify({"human_readable": human, "raw_json": raw}), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 413
    except Exception as e:
        return jsonify({"error": "Unexpected server error."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
