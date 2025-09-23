#!/usr/bin/env python3
"""
Smoke test for Ariadne Clew application.
Tests basic functionality end-to-end.
"""

import sys
import time
import requests
import subprocess
from pathlib import Path
from typing import Optional, Any

# Configuration
BACKEND_URL = "http://localhost:5001"
FRONTEND_URL = "http://localhost:8000"
TIMEOUT = 30  # seconds


class SmokeTest:
    def __init__(self) -> None:
        self.backend_process: Optional[subprocess.Popen[Any]] = None
        self.frontend_process: Optional[subprocess.Popen[Any]] = None
        self.success: bool = True
        self.errors: list[str] = []

    def log(self, message: str, is_error: bool = False) -> None:
        prefix = "❌ ERROR" if is_error else "✅ INFO"
        print(f"{prefix}: {message}")
        if is_error:
            self.errors.append(message)
            self.success = False

    def start_backend(self) -> bool:
        """Start the Flask backend server."""
        try:
            backend_dir = Path(__file__).parent / "backend"
            self.backend_process = subprocess.Popen(
                [sys.executable, "app.py"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.log("Backend process started")
            return True
        except Exception as e:
            self.log(f"Failed to start backend: {e}", is_error=True)
            return False

    def start_frontend(self) -> bool:
        """Start a simple HTTP server for frontend."""
        try:
            public_dir = Path(__file__).parent / "public"
            self.frontend_process = subprocess.Popen(
                [sys.executable, "-m", "http.server", "8000"],
                cwd=public_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.log("Frontend server started")
            return True
        except Exception as e:
            self.log(f"Failed to start frontend: {e}", is_error=True)
            return False

    def wait_for_service(self, url: str, service_name: str, timeout: int = TIMEOUT) -> bool:
        """Wait for a service to become available."""
        self.log(f"Waiting for {service_name} at {url}...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code in [200, 404]:
                    self.log(f"{service_name} is ready")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)

        self.log(f"{service_name} failed to start within {timeout}s", is_error=True)
        return False

    def test_backend_health(self) -> None:
        """Test that backend is responding."""
        try:
            response = requests.get(f"{BACKEND_URL}/nonexistent")
            if response.status_code == 404:
                self.log("Backend 404 handling works")
            else:
                self.log(
                    f"Backend unexpected status for 404 test: {response.status_code}",
                    is_error=True,
                )
        except Exception as e:
            self.log(f"Backend health check failed: {e}", is_error=True)

    def test_recap_api(self) -> None:
        """Test the main recap API endpoint."""
        test_cases: list[dict[str, Any]] = [
            {
                "name": "Valid request",
                "payload": {"chat_log": "Hello, this is a test conversation."},
                "expected_status": 200,
            },
            {
                "name": "Missing chat_log",
                "payload": {"wrong_field": "value"},
                "expected_status": 400,
            },
            {
                "name": "Invalid JSON",
                "payload": None,
                "expected_status": 400,
                "raw_data": "invalid json",
            },
            {
                "name": "Forbidden terms",
                "payload": {"chat_log": "Here is my password: secret123"},
                "expected_status": 400,
            },
        ]

        for test_case in test_cases:
            try:
                if test_case.get("raw_data"):
                    response = requests.post(
                        f"{BACKEND_URL}/recap",
                        data=test_case["raw_data"],
                        headers={"Content-Type": "application/json"},
                    )
                else:
                    response = requests.post(
                        f"{BACKEND_URL}/recap", json=test_case["payload"], timeout=10
                    )

                if response.status_code == test_case["expected_status"]:
                    self.log(f"API test '{test_case['name']}' passed")
                    if response.status_code == 200:
                        data = response.json()
                        if "human_readable" in data and "raw_json" in data:
                            self.log("Response structure is correct")
                        else:
                            self.log("Response missing required fields", is_error=True)
                else:
                    self.log(
                        f"API test '{test_case['name']}' failed: got {response.status_code}, expected {test_case['expected_status']}",
                        is_error=True,
                    )

            except Exception as e:
                self.log(f"API test '{test_case['name']}' error: {e}", is_error=True)

    def test_frontend_files(self) -> None:
        """Test that frontend files are accessible."""
        files_to_check: list[str] = [
            "/",
            "/index.html",
            "/styles/style.css",
            "/styles/theme.css",
            "/scripts/main.js",
            "/scripts/api.js",
        ]

        for file_path in files_to_check:
            try:
                response = requests.get(f"{FRONTEND_URL}{file_path}", timeout=5)
                if response.status_code == 200:
                    self.log(f"Frontend file accessible: {file_path}")
                else:
                    self.log(
                        f"Frontend file not accessible: {file_path} (status: {response.status_code})",
                        is_error=True,
                    )
            except Exception as e:
                self.log(
                    f"Error checking frontend file {file_path}: {e}", is_error=True
                )

    def cleanup(self) -> None:
        """Clean up processes."""
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()

        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()

        self.log("Cleanup completed")

    def run(self) -> bool:
        """Run the complete smoke test suite."""
        self.log("🚀 Starting Ariadne Clew smoke test")

        try:
            if not self.start_backend():
                return False

            if not self.start_frontend():
                return False

            if not self.wait_for_service(BACKEND_URL, "Backend"):
                return False

            if not self.wait_for_service(FRONTEND_URL, "Frontend"):
                return False

            self.test_backend_health()
            self.test_recap_api()
            self.test_frontend_files()

        finally:
            self.cleanup()

        if self.success:
            self.log("🎉 All smoke tests passed!")
            return True
        else:
            self.log("💥 Smoke tests failed!")
            self.log("Errors encountered:")
            for error in self.errors:
                self.log(f"  - {error}")
            return False


def main() -> None:
    """Main entry point."""
    smoke_test = SmokeTest()
    success = smoke_test.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
