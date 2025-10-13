# bridge_server.py - SIMPLIFIED VERSION
# Uses environment variables to disable Rich console formatting
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import json
import logging
import uuid
import os
import sys

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the full path to agentcore executable in venv
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_SCRIPTS = os.path.join(SCRIPT_DIR, '.venv', 'Scripts')
AGENTCORE_PATH = os.path.join(VENV_SCRIPTS, 'agentcore.exe')

if not os.path.exists(AGENTCORE_PATH):
    AGENTCORE_PATH = 'agentcore'
    logger.warning(f"agentcore.exe not found in venv, using PATH: {AGENTCORE_PATH}")
else:
    logger.info(f"Using agentcore from: {AGENTCORE_PATH}")

@app.route('/', methods=['GET'])
def serve_frontend():
    return send_from_directory('public', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('public', filename)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Ariadne Clew Bridge",
        "agentcore_ready": os.path.exists(AGENTCORE_PATH) if AGENTCORE_PATH.endswith('.exe') else True
    })

@app.route('/v1/recap', methods=['POST'])
def get_recap():
    try:
        data = request.json
        chat_log = data.get('chat_log', '')

        # ALWAYS generate proper session ID (AgentCore requires 33+ chars)
        provided_session = data.get('session_id', '')
        if provided_session and len(provided_session) >= 33:
            session_id = provided_session
        else:
            session_id = f'session-{uuid.uuid4()}'
            logger.info(f"Generated new session ID: {session_id}")

        logger.info(f"Processing recap for session: {session_id}")
        logger.info(f"Chat log length: {len(chat_log)} characters")

        # Validate input
        if not chat_log.strip():
            return jsonify({
                "error": "chat_log cannot be empty",
                "human_readable": "Please provide a chat transcript to analyze"
            }), 400

        if len(chat_log) > 200000:
            return jsonify({
                "error": "chat_log too large",
                "human_readable": "Chat transcript exceeds maximum length"
            }), 400

        # Prepare command
        agentcore_payload = {"prompt": chat_log}
        cmd = [
            AGENTCORE_PATH,
            'invoke',
            json.dumps(agentcore_payload),
            '--session-id', session_id
        ]

        logger.info(f"Executing AgentCore command...")

        # SIMPLE SOLUTION: Disable Rich formatting via environment variables
        env = os.environ.copy()
        env['NO_COLOR'] = '1'           # Disable colors
        env['TERM'] = 'dumb'            # Make rich think it's not a terminal
        env['PYTHONIOENCODING'] = 'utf-8'  # Use UTF-8 encoding

        # Execute with clean environment and UTF-8 encoding
        result = subprocess.run(
            cmd,
            capture_output=True,
            encoding='utf-8',      # Explicitly use UTF-8, not Windows cp1252
            errors='replace',      # Replace bad chars instead of crashing
            timeout=60,
            env=env
        )

        logger.info(f"AgentCore return code: {result.returncode}")

        # Safety check - if stdout is None, something went very wrong
        if result.stdout is None:
            logger.error("AgentCore stdout is None - encoding error likely occurred")
            logger.error(f"Stderr: {result.stderr}")
            return jsonify({
                "error": "Failed to read AgentCore output",
                "human_readable": "Unable to decode analysis results",
                "debug_details": {
                    "stderr": result.stderr[:500] if result.stderr else "None"
                }
            }), 500

        logger.info(f"Stdout length: {len(result.stdout)} chars")

        # SIMPLE PARSING: Rich outputs box, then "Response:", then JSON
        try:
            stdout = result.stdout
            logger.info(f"First 200 chars of stdout: {stdout[:200]}")

            # Find the Response: marker (comes after the pretty box)
            response_marker = "Response:"
            if response_marker in stdout:
                json_start = stdout.index(response_marker) + len(response_marker)
                remaining = stdout[json_start:].strip()
                logger.info(f"Found Response: marker, extracted {len(remaining)} chars after it")
            else:
                # No marker, look for first { after the box
                logger.warning("No Response: marker found, searching for JSON start")
                json_start = stdout.find('{"status"')
                if json_start == -1:
                    json_start = stdout.find('{')
                if json_start == -1:
                    raise ValueError("No JSON found in output")
                remaining = stdout[json_start:]
                logger.info(f"Found JSON at position {json_start}")

            # Extract first complete JSON object using brace counting
            brace_count = 0
            in_string = False
            escape = False
            end_pos = 0

            for i, char in enumerate(remaining):
                if escape:
                    escape = False
                    continue
                if char == '\\':
                    escape = True
                    continue
                if char == '"' and not escape:
                    in_string = not in_string
                    continue

                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and i > 0:  # Complete object
                            end_pos = i + 1
                            break

            if end_pos == 0:
                raise ValueError("Could not find complete JSON object")

            json_text = remaining[:end_pos]
            logger.info(f"Extracted JSON object ({len(json_text)} chars)")
            logger.info(f"JSON starts with: {json_text[:100]}")

            # CRITICAL: Fix literal newlines in JSON
            # Rich console outputs literal newlines which break JSON parsing
            # We need to escape them before json.loads()
            logger.info("Pre-processing JSON to escape literal newlines...")

            # Replace literal newlines with escaped \n, but only inside strings
            fixed_json = []
            in_string = False
            escape = False

            for i, char in enumerate(json_text):
                if escape:
                    fixed_json.append(char)
                    escape = False
                    continue

                if char == '\\':
                    fixed_json.append(char)
                    escape = True
                    continue

                if char == '"':
                    fixed_json.append(char)
                    in_string = not in_string
                    continue

                # Replace literal newlines/carriage returns in strings
                if in_string and char in ['\n', '\r']:
                    fixed_json.append('\\n')  # Escape it
                else:
                    fixed_json.append(char)

            json_text = ''.join(fixed_json)
            logger.info(f"Fixed JSON length: {len(json_text)} chars")
            logger.info(f"Fixed JSON starts with: {json_text[:100]}")

            # Now parse it
            agentcore_response = json.loads(json_text)
            logger.info("✓ Successfully parsed JSON")
            logger.info(f"Response keys: {list(agentcore_response.keys())}")

            # Extract result
            if 'result' in agentcore_response:
                agent_result = agentcore_response['result']
            else:
                agent_result = agentcore_response

            # Transform for frontend
            response = {
                "human_readable": agent_result.get('human_readable', 'Analysis completed'),
                "raw_json": agent_result.get('structured_data', {}),
                "session_id": session_id,
                "agent_metadata": agent_result.get('agent_metadata', {}),
                "status": "success"
            }

            logger.info("✓ Successfully transformed response")
            return jsonify(response)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.error(f"Failed at position {e.pos}")
            logger.error(f"Stdout: {result.stdout[:1000]}")

            return jsonify({
                "error": "Failed to parse AgentCore response",
                "human_readable": "Analysis completed but response format was unexpected",
                "debug_details": {
                    "parse_error": str(e),
                    "stdout_preview": result.stdout[:500]
                }
            }), 500

    except subprocess.TimeoutExpired:
        logger.error("AgentCore execution timed out")
        return jsonify({
            "error": "Analysis timeout",
            "human_readable": "Analysis took too long, please try with shorter input"
        }), 408

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "human_readable": "An unexpected error occurred",
            "debug_error": str(e)
        }), 500

@app.route('/v1/status', methods=['GET'])
def get_status():
    try:
        result = subprocess.run([AGENTCORE_PATH, '--version'], capture_output=True, text=True, timeout=5)
        agentcore_available = result.returncode == 0

        return jsonify({
            "bridge_server": "running",
            "agentcore_available": agentcore_available,
            "agentcore_version": result.stdout.strip() if agentcore_available else "unavailable",
            "agentcore_path": AGENTCORE_PATH
        })

    except Exception as e:
        return jsonify({
            "bridge_server": "running",
            "agentcore_available": False,
            "agentcore_path": AGENTCORE_PATH,
            "error": str(e)
        })

if __name__ == '__main__':
    print("🧶 Ariadne Clew Bridge Server Starting...")
    print("📡 Frontend API: http://localhost:5000")
    print(f"🔗 AgentCore path: {AGENTCORE_PATH}")
    print("🔗 Connecting to AgentCore backend...")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False  # Disabled to prevent restart loops
    )
