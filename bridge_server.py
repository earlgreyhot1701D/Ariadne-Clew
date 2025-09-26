# bridge_server.py - Connects your polished frontend to working AgentCore backend
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import json
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend connection

# Configure logging for demo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET'])
def serve_frontend():
    """Serve the frontend from public/ folder"""
    return send_from_directory('public', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from public/ folder"""
    return send_from_directory('public', filename)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for demo"""
    return jsonify({
        "status": "healthy",
        "service": "Ariadne Clew Bridge",
        "agentcore_ready": True
    })

@app.route('/v1/recap', methods=['POST'])
def get_recap():
    """
    Bridge endpoint that connects frontend to AgentCore backend
    Transforms REST API call into AgentCore invoke command
    """
    try:
        # Get request data
        data = request.json
        chat_log = data.get('chat_log', '')
        session_id = data.get('session_id', f'demo-{hash(chat_log) % 10000}')

        logger.info(f"Processing recap request for session: {session_id}")
        logger.info(f"Chat log length: {len(chat_log)} characters")

        # Validate input
        if not chat_log.strip():
            return jsonify({
                "error": "chat_log cannot be empty",
                "human_readable": "Please provide a chat transcript to analyze"
            }), 400

        if len(chat_log) > 50000:  # Reasonable limit for demo
            return jsonify({
                "error": "chat_log too large",
                "human_readable": "Chat transcript exceeds maximum length"
            }), 400

        # Call your working AgentCore agent
        agentcore_payload = {"prompt": chat_log}

        cmd = [
            'agentcore', 'invoke',
            json.dumps(agentcore_payload),
            '--session-id', session_id
        ]

        logger.info(f"Executing AgentCore command: {' '.join(cmd[:3])}...")

        # Execute with timeout for demo reliability
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )

        if result.returncode == 0:
            logger.info("AgentCore execution successful")

            # Parse AgentCore response
            try:
                agentcore_response = json.loads(result.stdout)

                # Transform to frontend expected format
                response = {
                    "human_readable": agentcore_response.get('summary', 'Analysis completed successfully'),
                    "raw_json": {
                        "aha_moments": agentcore_response.get('aha_moments', []),
                        "code_snippets": agentcore_response.get('code_snippets', []),
                        "mvp_changes": agentcore_response.get('mvp_changes', []),
                        "design_tradeoffs": agentcore_response.get('design_tradeoffs', []),
                        "full_analysis": agentcore_response
                    },
                    "session_id": session_id,
                    "timestamp": agentcore_response.get('timestamp'),
                    "status": "success"
                }

                return jsonify(response)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AgentCore response: {e}")
                return jsonify({
                    "error": "Invalid response from AgentCore",
                    "human_readable": "Analysis service returned invalid data",
                    "debug_output": result.stdout[:500]  # First 500 chars for debugging
                }), 500

        else:
            logger.error(f"AgentCore failed with return code {result.returncode}")
            logger.error(f"AgentCore stderr: {result.stderr}")

            return jsonify({
                "error": f"AgentCore execution failed (code {result.returncode})",
                "human_readable": "Analysis service is currently unavailable",
                "debug_stderr": result.stderr[:500]  # For demo debugging
            }), 500

    except subprocess.TimeoutExpired:
        logger.error("AgentCore execution timed out")
        return jsonify({
            "error": "Analysis timeout",
            "human_readable": "Analysis is taking too long, please try with shorter input"
        }), 408

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "human_readable": "An unexpected error occurred during analysis",
            "debug_error": str(e)
        }), 500

@app.route('/v1/status', methods=['GET'])
def get_status():
    """Demo endpoint showing system status"""
    try:
        # Test AgentCore availability
        result = subprocess.run(['agentcore', '--version'], capture_output=True, text=True, timeout=5)
        agentcore_available = result.returncode == 0

        return jsonify({
            "bridge_server": "running",
            "agentcore_available": agentcore_available,
            "agentcore_version": result.stdout.strip() if agentcore_available else "unavailable"
        })

    except Exception as e:
        return jsonify({
            "bridge_server": "running",
            "agentcore_available": False,
            "error": str(e)
        })

if __name__ == '__main__':
    print("🧶 Ariadne Clew Bridge Server Starting...")
    print("📡 Frontend API: http://localhost:5000")
    print("🔗 Connecting to AgentCore backend...")

    app.run(
        host='0.0.0.0',  # Allow external connections for demo
        port=5000,
        debug=True  # Enable for demo debugging
    )
