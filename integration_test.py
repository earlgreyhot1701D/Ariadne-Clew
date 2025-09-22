#!/usr/bin/env python3
"""
Integration test for Ariadne Clew full pipeline.
Tests the actual agent workflow: filters → classifier → code_handler → diff → recap_formatter → memory
"""

import sys
import time
import requests
import subprocess
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

class AriadneIntegrationTest:
    def __init__(self):
        self.backend_process = None
        self.success = True
        self.errors = []
        self.test_session_id = "integration-test-001"

    def log(self, message, is_error=False):
        prefix = "❌ ERROR" if is_error else "✅ INFO"
        print(f"{prefix}: {message}")
        if is_error:
            self.errors.append(message)
            self.success = False

    def start_backend_api(self):
        """Start the main API recap server."""
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, "api_recap.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "LOG_LEVEL": "INFO"}
            )
            self.log("Main API server started")
            return True
        except Exception as e:
            self.log(f"Failed to start API server: {e}", is_error=True)
            return False

    def wait_for_api(self, url="http://localhost:5000", timeout=30):
        """Wait for the API to become ready."""
        self.log(f"Waiting for API at {url}...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Try a simple health check
                response = requests.get(f"{url}/nonexistent", timeout=5)
                if response.status_code == 404:  # Expected for non-existent endpoint
                    self.log("API server is ready")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        self.log(f"API failed to start within {timeout}s", is_error=True)
        return False

    def test_full_pipeline(self):
        """Test the complete Ariadne pipeline with a realistic chat log."""
        
        # Realistic test data that exercises the full pipeline
        test_chat_log = """
        User: I need a function to calculate fibonacci numbers

        Assistant: Here's a recursive implementation:
        ```python
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        ```

        User: That looks good but won't it be slow for large numbers?

        Assistant: You're absolutely right! The recursive approach has exponential time complexity. Here's a better iterative version:
        ```python
        def fibonacci(n):
            if n <= 1:
                return n
            a, b = 0, 1
            for i in range(2, n + 1):
                a, b = b, a + b
            return b
        ```

        User: Perfect! This is my final version.

        Assistant: Great choice! The iterative approach is much more efficient with O(n) time complexity.
        """

        try:
            # Mock AWS services for testing
            with patch('api_recap.bedrock') as mock_bedrock, \
                 patch('api_recap.store_recap') as mock_store:
                
                # Mock Bedrock response
                mock_response = {
                    "body": MagicMock()
                }
                mock_response["body"].read.return_value.decode.return_value = json.dumps({
                    "blocks": [
                        {"type": "text", "content": "User: I need a function to calculate fibonacci numbers"},
                        {"type": "code", "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"},
                        {"type": "text", "content": "User: That looks good but won't it be slow for large numbers?"},
                        {"type": "code", "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for i in range(2, n + 1):\n        a, b = b, a + b\n    return b"},
                        {"type": "text", "content": "User: Perfect! This is my final version."}
                    ]
                })
                mock_bedrock.invoke_model.return_value = mock_response
                
                # Make the API call
                response = requests.post(
                    "http://localhost:5000/v1/recap",
                    json={"chat_log": test_chat_log},
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    self.log("✅ Full pipeline test passed")
                    data = response.json()
                    
                    # Validate response structure
                    required_fields = ["final", "rejected", "text_summary"]
                    for field in required_fields:
                        if field not in data:
                            self.log(f"Missing field in response: {field}", is_error=True)
                        else:
                            self.log(f"✅ Response contains {field}")
                    
                    # Validate that we got the final version
                    if "final" in data and data["final"].get("content"):
                        self.log("✅ Final code snippet captured")
                    else:
                        self.log("❌ No final code snippet in response", is_error=True)
                    
                    # Check that memory store was called
                    if mock_store.called:
                        self.log("✅ Memory storage was invoked")
                    else:
                        self.log("❌ Memory storage not called", is_error=True)
                        
                else:
                    self.log(f"API call failed with status {response.status_code}", is_error=True)
                    self.log(f"Response: {response.text}", is_error=True)
                    
        except Exception as e:
            self.log(f"Pipeline test failed: {e}", is_error=True)

    def test_filter_pipeline(self):
        """Test the filtering and validation pipeline."""
        test_cases = [
            {
                "name": "Valid input",
                "chat_log": "```python\nprint('hello')\n```",
                "should_succeed": True
            },
            {
                "name": "Input with PII",
                "chat_log": "Contact me at test@example.com for the code: ```python\nprint('hello')\n```",
                "should_succeed": True  # Should succeed but PII should be scrubbed
            },
            {
                "name": "Input with forbidden terms",
                "chat_log": "Here's my password: secret123",
                "should_succeed": False
            },
            {
                "name": "Oversized input",
                "chat_log": "x" * 200000,  # Over the limit
                "should_succeed": False
            }
        ]

        for test_case in test_cases:
            try:
                response = requests.post(
                    "http://localhost:5000/v1/recap",
                    json={"chat_log": test_case["chat_log"]},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if test_case["should_succeed"]:
                    if response.status_code == 200:
                        self.log(f"✅ Filter test '{test_case['name']}' passed")
                    else:
                        self.log(f"❌ Filter test '{test_case['name']}' should have succeeded but got {response.status_code}", is_error=True)
                else:
                    if response.status_code != 200:
                        self.log(f"✅ Filter test '{test_case['name']}' correctly rejected")
                    else:
                        self.log(f"❌ Filter test '{test_case['name']}' should have been rejected", is_error=True)
                        
            except Exception as e:
                self.log(f"Filter test '{test_case['name']}' error: {e}", is_error=True)

    def test_schema_validation(self):
        """Test that schema validation is working."""
        try:
            from schema import validate_recap_output
            
            # Test valid schema
            valid_data = {
                "final": {
                    "version": 1,
                    "snippet_id": "test_1",
                    "content": "print('test')",
                    "diff_summary": "Initial version"
                },
                "rejected": [],
                "text_summary": "Test summary"
            }
            
            if validate_recap_output(valid_data):
                self.log("✅ Schema validation working correctly")
            else:
                self.log("❌ Schema validation failed for valid data", is_error=True)
                
        except Exception as e:
            self.log(f"Schema validation test error: {e}", is_error=True)

    def cleanup(self):
        """Clean up processes."""
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        self.log("Cleanup completed")

    def run(self):
        """Run the complete integration test suite."""
        self.log("🧶 Starting Ariadne Clew Integration Tests")
        
        try:
            # Start the main API server
            if not self.start_backend_api():
                return False
            
            # Wait for API to be ready
            if not self.wait_for_api():
                return False
            
            # Run the test suite
            self.test_schema_validation()
            self.test_filter_pipeline() 
            self.test_full_pipeline()
            
        finally:
            self.cleanup()
        
        # Report results
        if self.success:
            self.log("🎉 All integration tests passed!")
            self.log("Your Ariadne Clew agent is ready for the hackathon!")
            return True
        else:
            self.log("💥 Some integration tests failed!")
            self.log("Issues found:")
            for error in self.errors:
                self.log(f"  - {error}")
            return False

def main():
    """Main entry point."""
    test = AriadneIntegrationTest()
    success = test.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()