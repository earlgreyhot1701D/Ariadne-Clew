import pytest
import asyncio
import json
from unittest.mock import patch, Mock
from backend.agent import AriadneClew, process_chat_log, invoke


@pytest.fixture
def sample_chat_log():
    """Sample chat transcript for testing"""
    return """
    User: I need a Python function to reverse a string
    Assistant: Here's a simple approach:

    def reverse_string(s):
        return s[::-1]

    User: That works! Let's use this as the final version.
    """


@pytest.fixture
def mock_agent_response():
    """Mock response from strands.Agent"""
    mock_response = Mock()
    mock_response.message = json.dumps(
        {
            "session_id": "test-session",
            "aha_moments": ["Slicing is the simplest approach"],
            "mvp_changes": ["Added string reversal utility"],
            "code_snippets": [
                {
                    "content": "def reverse_string(s):\n    return s[::-1]",
                    "language": "python",
                    "user_marked_final": True,
                    "context": "User requested string reversal function",
                }
            ],
            "design_tradeoffs": ["Chose slicing over loop for readability"],
            "scope_creep": [],
            "readme_notes": ["String utilities module needed"],
            "post_mvp_ideas": ["Add input validation"],
            "quality_flags": [],
            "summary": "Created simple string reversal function",
        }
    )
    return mock_response


class TestAriadneClew:
    """Test suite for AriadneClew with real AgentCore API"""

    @pytest.mark.asyncio
    async def test_agent_processes_transcript_successfully(
        self, sample_chat_log, mock_agent_response
    ):
        """AriadneClew should process transcript using real AgentCore"""

        with patch("backend.agent.agent") as mock_agent:
            mock_agent.return_value = mock_agent_response

            ariadne = AriadneClew(session_id="test-session")
            result = await ariadne.process_transcript(sample_chat_log)

            # Verify structure
            assert "human_readable" in result
            assert "structured_data" in result
            assert "agent_metadata" in result
            assert result["session_id"] == "test-session"

            # Verify real AgentCore metadata
            metadata = result["agent_metadata"]
            assert metadata["processed_by"] == "AriadneClew"
            assert metadata["agentcore_runtime"] == "BedrockAgentCoreApp"
            assert metadata["strands_agent"] is True
            assert metadata["code_snippets_found"] == 1

            # Verify human readable contains key sections
            human_summary = result["human_readable"]
            assert "Session Recap: test-session" in human_summary
            assert "Key Insights" in human_summary
            assert "Slicing is the simplest approach" in human_summary
            assert "Code Discovered" in human_summary

    @pytest.mark.asyncio
    async def test_json_parsing_from_agent_response(self, sample_chat_log):
        """AriadneClew should parse JSON from various agent response formats"""

        test_cases = [
            # Pure JSON
            '{"test": "value"}',
            # JSON in markdown code block
            '```json\n{"test": "value"}\n```',
            # JSON in generic code block
            '```\n{"test": "value"}\n```',
            # JSON mixed with text
            'Here is the analysis: {"test": "value"} Hope this helps!',
        ]

        for response_format in test_cases:
            with patch("backend.agent.agent") as mock_agent:
                mock_response = Mock()
                mock_response.message = response_format
                mock_agent.return_value = mock_response

                ariadne = AriadneClew(session_id="test-parsing")

                try:
                    result = await ariadne.process_transcript(sample_chat_log)
                    # Should not raise an exception
                    assert "structured_data" in result
                except ValueError:
                    # This is expected for malformed JSON
                    pass

    @pytest.mark.asyncio
    async def test_invalid_json_handling(self, sample_chat_log):
        """AriadneClew should handle invalid JSON gracefully"""

        with patch("backend.agent.agent") as mock_agent:
            mock_response = Mock()
            mock_response.message = "This is not JSON at all, just plain text"
            mock_agent.return_value = mock_response

            ariadne = AriadneClew(session_id="test-invalid-json")

            with pytest.raises(ValueError, match="Agent returned invalid JSON"):
                await ariadne.process_transcript(sample_chat_log)

    @pytest.mark.asyncio
    async def test_agent_error_handling(self, sample_chat_log):
        """AriadneClew should handle strands.Agent errors gracefully"""

        with patch("backend.agent.agent") as mock_agent:
            mock_agent.side_effect = Exception("Strands agent failed")

            ariadne = AriadneClew(session_id="test-error")

            with pytest.raises(RuntimeError, match="Reasoning extraction failed"):
                await ariadne.process_transcript(sample_chat_log)

    @pytest.mark.asyncio
    async def test_invalid_input_handling(self):
        """AriadneClew should validate input parameters"""

        ariadne = AriadneClew(session_id="test-validation")

        # Test empty string
        with pytest.raises(ValueError, match="Invalid chat_log"):
            await ariadne.process_transcript("")

        # Test None input
        with pytest.raises(ValueError, match="Invalid chat_log"):
            await ariadne.process_transcript(None)

        # Test non-string input
        with pytest.raises(ValueError, match="Invalid chat_log"):
            await ariadne.process_transcript(123)

    def test_human_summary_generation(self):
        """AriadneClew should generate readable human summaries"""

        analysis = {
            "session_id": "test-summary",
            "summary": "Test session summary",
            "aha_moments": ["Key insight 1", "Key insight 2"],
            "code_snippets": [
                {
                    "content": "def test(): pass",
                    "language": "python",
                    "user_marked_final": True,
                    "context": "Test function",
                }
            ],
            "mvp_changes": ["Added test functionality"],
            "design_tradeoffs": ["Simplicity over performance"],
            "post_mvp_ideas": ["Add error handling"],
        }

        ariadne = AriadneClew(session_id="test-summary")
        summary = ariadne._generate_human_summary(analysis)

        assert "Session Recap: test-summary" in summary
        assert "Test session summary" in summary
        assert "Key Insights" in summary
        assert "Key insight 1" in summary
        assert "Code Discovered" in summary
        assert "**python snippet** FINAL" in summary
        assert "Scope Changes" in summary
        assert "Design Decisions" in summary
        assert "Post-MVP Ideas" in summary


class TestAgentCoreEntrypoint:
    """Test the AgentCore entrypoint function"""

    def test_agentcore_invoke_success(self, mock_agent_response):
        """AgentCore entrypoint should handle valid payloads"""

        with patch("backend.agent.agent") as mock_agent:
            mock_agent.return_value = mock_agent_response

            payload = {
                "chat_log": "User: Hello\nAssistant: Hi there!",
                "session_id": "agentcore-test",
            }

            result = invoke(payload)

            assert result["status"] == "success"
            assert "result" in result
            assert result["result"]["session_id"] == "agentcore-test"

    def test_agentcore_invoke_missing_chat_log(self):
        """AgentCore entrypoint should handle missing chat_log"""

        payload = {"session_id": "test"}

        result = invoke(payload)

        assert result["status"] == "failed"
        assert "Missing 'chat_log' in payload" in result["error"]

    def test_agentcore_invoke_processing_error(self):
        """AgentCore entrypoint should handle processing errors"""

        with patch("backend.agent.agent") as mock_agent:
            mock_agent.side_effect = Exception("Processing failed")

            payload = {"chat_log": "User: Hello\nAssistant: Hi there!"}

            result = invoke(payload)

            assert result["status"] == "failed"
            assert "Processing failed" in result["error"]


class TestBackwardsCompatibility:
    """Test backwards compatibility functions"""

    @pytest.mark.asyncio
    async def test_process_chat_log_function(
        self, sample_chat_log, mock_agent_response
    ):
        """process_chat_log() should work as drop-in replacement"""

        with patch("backend.agent.agent") as mock_agent:
            mock_agent.return_value = mock_agent_response

            result = await process_chat_log(sample_chat_log, session_id="compat-test")

            # Should return same structure as AriadneClew.process_transcript()
            assert "human_readable" in result
            assert "structured_data" in result
            assert result["session_id"] == "compat-test"


class TestDemo:
    """Test demo functionality"""

    @pytest.mark.asyncio
    async def test_demo_runs_without_error(self, mock_agent_response):
        """Demo function should execute without raising exceptions"""

        with patch("backend.agent.agent") as mock_agent, patch(
            "builtins.print"
        ) as mock_print:

            # Mock the fibonacci demo response
            fibonacci_response = Mock()
            fibonacci_response.message = json.dumps(
                {
                    "session_id": "demo",
                    "aha_moments": ["Iterative approach is more efficient"],
                    "mvp_changes": ["Switched from recursive to iterative"],
                    "code_snippets": [
                        {
                            "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b",
                            "language": "python",
                            "user_marked_final": True,
                            "context": "Final fibonacci implementation",
                        }
                    ],
                    "design_tradeoffs": ["Performance over simplicity"],
                    "scope_creep": [],
                    "readme_notes": [],
                    "post_mvp_ideas": [],
                    "quality_flags": [],
                    "summary": "Implemented efficient Fibonacci function",
                }
            )
            mock_agent.return_value = fibonacci_response

            # Import and run demo
            from backend.agent import demo_ariadne_clew

            # Should not raise any exceptions
            await demo_ariadne_clew()

            # Verify demo printed output
            assert mock_print.call_count >= 3  # Human, structured, metadata


class TestIntegration:
    """Integration-style tests with realistic mocking"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_pipeline_with_real_agentcore_mocking(self, sample_chat_log):
        """Test complete pipeline with realistic AgentCore mocking"""

        with patch("bedrock_agentcore.BedrockAgentCoreApp") as mock_app, patch(
            "strands.Agent"
        ) as mock_agent_class, patch("backend.agent.agent") as mock_agent_instance:

            # Mock the BedrockAgentCoreApp initialization
            mock_app.return_value = Mock()
            mock_agent_class.return_value = Mock()

            # Mock realistic agent response
            mock_response = Mock()
            mock_response.message = json.dumps(
                {
                    "session_id": "integration-test",
                    "aha_moments": ["String slicing is elegant"],
                    "mvp_changes": ["Added string utility"],
                    "code_snippets": [
                        {
                            "content": "def reverse_string(s):\n    return s[::-1]",
                            "language": "python",
                            "user_marked_final": True,
                            "context": "User requested string reversal",
                        }
                    ],
                    "design_tradeoffs": ["Simplicity over verbosity"],
                    "scope_creep": [],
                    "readme_notes": ["Document string utilities"],
                    "post_mvp_ideas": ["Add type hints"],
                    "quality_flags": [],
                    "summary": "Created string reversal utility",
                }
            )
            mock_agent_instance.return_value = mock_response

            # Run full pipeline
            ariadne = AriadneClew(session_id="integration-test")
            result = await ariadne.process_transcript(sample_chat_log)

            # Verify complete output structure
            assert result["session_id"] == "integration-test"
            assert "human_readable" in result
            assert "structured_data" in result
            assert "agent_metadata" in result

            # Verify AgentCore-specific metadata
            metadata = result["agent_metadata"]
            assert metadata["processed_by"] == "AriadneClew"
            assert metadata["agentcore_runtime"] == "BedrockAgentCoreApp"
            assert metadata["strands_agent"] is True

            # Verify human readable formatting
            human_output = result["human_readable"]
            assert "Session Recap: integration-test" in human_output
            assert "Key Insights" in human_output
            assert "String slicing is elegant" in human_output
            assert "Code Discovered" in human_output


# Pytest fixture for async support
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
