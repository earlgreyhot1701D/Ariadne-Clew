# Troubleshooting Guide

**For AWS Agent Hackathon Judges & Developers**

Having issues getting AriadneClew running? This guide covers common problems and their solutions.

---

## 🚀 Quick Start Checklist

Before reporting issues, verify these essentials:

- [ ] **Python 3.11+** installed: `python --version`
- [ ] **AWS credentials** configured: `aws sts get-caller-identity`
- [ ] **AgentCore CLI** installed: `agentcore --version`
- [ ] **Dependencies** installed: `pip install -r requirements.txt`
- [ ] **Bedrock access** enabled in your AWS account (us-east-1 recommended)
- [ ] **Bridge server** running: `python bridge_server.py`

---

## 🔧 Common Issues

### Issue #1: AgentCore Module Not Found

**Error Message:**

```
ModuleNotFoundError: No module named 'bedrock_agentcore'
```

**Cause:** AgentCore SDK not installed or not in Python path

**Solution:**

```bash
# Install AgentCore SDK
pip install bedrock-agentcore strands-agents --break-system-packages

# Verify installation
agentcore --version

# If still failing, check Python path
python -c "import bedrock_agentcore; print(bedrock_agentcore.__file__)"
```

**Alternative (Virtual Environment):**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install bedrock-agentcore strands-agents
```

---

### Issue #2: AWS Credentials Not Configured

**Error Message:**

```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

**Cause:** AWS CLI not configured or credentials expired

**Solution:**

**Option 1: AWS CLI Configuration (Recommended)**

```bash
aws configure
# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Output format: json

# Verify it works
aws sts get-caller-identity
```

**Option 2: Environment Variables**

```bash
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_DEFAULT_REGION=us-east-1

# On Windows:
set AWS_ACCESS_KEY_ID=
set AWS_SECRET_ACCESS_KEY=
set AWS_DEFAULT_REGION=us-east-1
```

**Option 3: AWS Profile**

```bash
# If you have multiple AWS profiles
export AWS_PROFILE=your-profile-name

# Or set in code
aws configure --profile hackathon
export AWS_PROFILE=hackathon
```

---

### Issue #3: Bedrock Access Denied

**Error Message:**

```
An error occurred (AccessDeniedException) when calling the InvokeModel operation:
You don't have access to the model with the specified model ID.
```

**Cause:** Bedrock not enabled in your account or region, or insufficient IAM permissions

**Solution:**

**Step 1: Enable Bedrock Model Access**

1. Go to AWS Console → Bedrock → Model access
2. Click "Manage model access"
3. Select "Claude" models (specifically Claude Sonnet 3.5)
4. Click "Request model access"
5. Wait 2-5 minutes for approval

**Step 2: Verify Region**

```bash
# Bedrock is available in specific regions
# Recommended: us-east-1

# Check your current region
aws configure get region

# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

**Step 3: Check IAM Permissions**

Your IAM user/role needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
    }
  ]
}
```

---

### Issue #4: AgentCore Configuration Issues

**Error Message:**

```
Error: No entrypoint configured
# or
Error: Could not find .bedrock_agentcore.yaml
```

**Cause:** AgentCore not properly configured for the project

**Solution:**

```bash
# Configure AgentCore for this project
cd /path/to/Ariadne-Clew
agentcore configure --entrypoint backend/agent.py

# This creates .bedrock_agentcore.yaml with your settings

# Verify configuration
cat .bedrock_agentcore.yaml

# Test the agent
agentcore invoke '{"prompt":"User: test\nAssistant: response"}' --session-id test
```

**If Configuration Keeps Resetting:**

```bash
# Remove cached config
rm .bedrock_agentcore.yaml

# Reconfigure with force
agentcore configure --entrypoint backend/agent.py --force

# Launch with auto-update
agentcore launch --auto-update-on-conflict
```

---

### Issue #5: Bridge Server Won't Start

**Error Message:**

```
OSError: [Errno 48] Address already in use
# or
ModuleNotFoundError: No module named 'flask'
```

**Cause:** Port 5000 already in use, or Flask not installed

**Solution:**

**If Port is Busy:**

```bash
# Find what's using port 5000
lsof -i :5000  # On Mac/Linux
netstat -ano | findstr :5000  # On Windows

# Kill the process or use a different port
export PORT=5001
python bridge_server.py

# Update frontend to use new port
# Edit public/scripts/api_js.js: change localhost:5000 to localhost:5001
```

**If Flask Missing:**

```bash
pip install flask flask-cors

# Verify
python -c "import flask; print(flask.__version__)"
```

---

### Issue #6: Frontend Not Loading

**Error Message:**

```
This site can't be reached
# or
Failed to fetch
```

**Cause:** Bridge server not running, or browser cache issues

**Solution:**

**Step 1: Verify Bridge Server**

```bash
# Start the bridge server
python bridge_server.py

# You should see:
# * Running on http://0.0.0.0:5000
# * Running on http://127.0.0.1:5000

# Test health endpoint
curl http://localhost:5000/health
# Should return: {"status": "healthy", ...}
```

**Step 2: Check Browser Console**

1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for errors (red text)
4. Common issues:
   - CORS errors → Bridge server not running
   - 404 errors → Wrong URL
   - Network errors → Firewall blocking

**Step 3: Try Different URL**

```
Try each of these:
✓ http://localhost:5000
✓ http://127.0.0.1:5000
✓ http://0.0.0.0:5000
```

**Step 4: Clear Browser Cache**

```
Chrome/Edge: Ctrl+Shift+Delete → Clear cache
Firefox: Ctrl+Shift+Delete → Clear cache
Safari: Cmd+Option+E → Empty caches
```

---

### Issue #7: Tests Failing

**Error Message:**

```
pytest: command not found
# or
ImportError: No module named 'pytest'
# or
Tests failing with AWS credential errors
```

**Cause:** Testing dependencies not installed, or tests need AWS credentials

**Solution:**

**Install Test Dependencies:**

```bash
pip install pytest pytest-asyncio pytest-mock

# Run tests
pytest tests/ -v
```

**Tests Requiring AWS (Optional):**
Most tests use mocked Bedrock calls and don't need real AWS credentials.

**Run Only Tests That Don't Need AWS:**

```bash
# These tests work without AWS credentials
pytest tests/test_schema.py -v
pytest tests/test_filters.py -v
pytest tests/test_diffcheck.py -v
pytest tests/test_code_handler.py -v
```

**Run Full Suite (Requires AWS):**

```bash
# Configure AWS credentials first
export AWS_PROFILE=your-profile

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

---

### Issue #8: Slow Processing / Timeouts

**Error Message:**

```
TimeoutError: Request took too long
# or
Processing took longer than expected
```

**Cause:** Large transcript, slow network, or Bedrock API throttling

**Solution:**

**Check Transcript Size:**

```bash
# Transcripts over 50K characters will be rejected
echo "Transcript length: $(wc -c < your_transcript.txt)"

# If too large, split into chunks
head -n 1000 your_transcript.txt > chunk1.txt
tail -n 1000 your_transcript.txt > chunk2.txt
```

**Increase Timeout:**

```python
# In bridge_server.py, line ~78
result = subprocess.run(
    cmd,
    capture_output=True,
    text=True,
    timeout=120  # Increase from 60 to 120 seconds
)
```

**Check Bedrock Latency:**

```bash
# Test direct Bedrock call
time aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-sonnet-3-5-20240620-v2:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","messages":[{"role":"user","content":"test"}],"max_tokens":100}' \
  output.json

# Should complete in 1-3 seconds for simple prompts
```

**If Consistently Slow:**

- Check if you're in a supported region (us-east-1 is fastest)
- Verify network connectivity to AWS
- Check Bedrock service health: https://status.aws.amazon.com

---

### Issue #9: Invalid JSON Output

**Error Message:**

```
json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
# or
ValidationError: extra fields not permitted
```

**Cause:** LLM returned malformed JSON, or response doesn't match schema

**Solution:**

**Check AgentCore Logs:**

```bash
# Run with verbose logging
agentcore invoke '{"prompt":"test"}' --session-id test --verbose

# Look for the actual LLM response in logs
# Should be valid JSON matching the schema
```

**Test Prompt Directly:**

```bash
# Test your reasoning extraction prompt
cat prompts/classifier_prompt.md

# Verify it asks for valid JSON output
# Should include: "Return ONLY valid JSON"
```

**If Validation Fails:**

```python
# The schema is strict (extra="forbid")
# Check backend/schema.py for required fields

# Common issues:
# - LLM adds extra fields → Schema rejects it
# - LLM returns null instead of [] → Schema catches it
# - LLM returns string instead of list → Schema catches it
```

**Temporary Workaround:**

```python
# In backend/agent.py, add more lenient parsing:
try:
    recap = Recap.model_validate(analysis)
except ValidationError as e:
    logger.warning(f"Validation failed, using fallback: {e}")
    # Return minimal valid structure
    return {
        "aha_moments": analysis.get("aha_moments", []),
        "summary": analysis.get("summary", "Processing completed with warnings"),
        # ... other fields with defaults
    }
```

---

## 🧪 Testing Your Setup

### Minimal Working Test

Run this to verify everything works:

```bash
# Test 1: AgentCore is configured
agentcore --version
# Expected: AgentCore CLI version X.X.X

# Test 2: AWS credentials work
aws sts get-caller-identity
# Expected: Account details (no errors)

# Test 3: Bedrock access works
aws bedrock list-foundation-models --region us-east-1 | grep claude
# Expected: List of Claude models

# Test 4: Python imports work
python -c "from bedrock_agentcore import BedrockAgentCoreApp; print('✓ AgentCore SDK installed')"
# Expected: ✓ AgentCore SDK installed

# Test 5: Bridge server starts
python bridge_server.py &
sleep 2
curl http://localhost:5000/health
# Expected: {"status": "healthy", ...}

# Test 6: End-to-end test
agentcore invoke '{"prompt":"User: I need auth\nAssistant: Use sessions"}' --session-id test
# Expected: Structured JSON with aha_moments, summary, etc.
```

If all 6 tests pass, AriadneClew is working correctly!

---

## 🔍 Advanced Debugging

### Enable Verbose Logging

```python
# In bridge_server.py or backend/agent.py
import logging
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Inspect AgentCore Execution

```bash
# Run AgentCore with debug output
agentcore invoke '{"prompt":"test"}' --session-id debug --verbose

# Check AgentCore logs
ls ~/.bedrock_agentcore/logs/
tail -f ~/.bedrock_agentcore/logs/latest.log
```

### Test Individual Components

```bash
# Test filters
python -c "from backend.filters import scrub_pii; print(scrub_pii('email: test@example.com'))"

# Test schema
python -c "from backend.schema import Recap; print(Recap(session_id='test', summary='test'))"

# Test code handler
python -c "from backend.code_handler import validate_snippet; print(validate_snippet('print(1)'))"
```

---

## 💬 Still Stuck?

### Gather Debug Information

Before asking for help, collect this info:

```bash
# System info
python --version
pip list | grep -E 'bedrock|strands|flask|pydantic'
agentcore --version

# AWS info
aws configure get region
aws sts get-caller-identity

# Error logs
agentcore invoke '{"prompt":"test"}' --session-id debug --verbose 2>&1 | tail -50

# Project structure
tree -L 2 -I '__pycache__|*.pyc|venv'
```

### Contact

- **GitHub Issues**: [Your repo URL]/issues
- **AWS Agent Hackathon**: Devpost discussion forum
- **Email**: lsjcordero@gmail.com (for judges/reviewers only)

### Known Limitations (MVP)

These are intentional scope limitations, not bugs:

- ✓ Code validation is syntax-only (AST parsing)
- ✓ Memory is local files (not AgentCore Memory API)
- ✓ Single-user only (no authentication)
- ✓ English transcripts only (no i18n)
- ✓ 50K character limit on transcripts

These will be addressed post-MVP with AgentCore tools integration.

---

## 📚 Additional Resources

- **AgentCore Docs**: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-agentcore.html
- **Bedrock Docs**: https://docs.aws.amazon.com/bedrock/
- **Project README**: [../README.md](../README.md)
- **Architecture Docs**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Test Suite**: Run `pytest tests/ -v` to see all test cases

---

**Last Updated:** October 2, 2025  
**For:** AWS Agent Hackathon Judges & Developers  
**Status:** Production-ready troubleshooting guide
