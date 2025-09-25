import pytest
import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch
from agent import AriadneClew, process_chat_log
from backend.schema import Recap


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
def mock_agentcore_response():
    """Mock structured response from AgentCore agent"""
    return {
        "session_id": "test-session",
        "aha_moments": ["Slicing is the simplest approach"],
        "mvp_changes": ["Added string reversal utility"],
        "code_snippets": [
            {
                "content": "def reverse_string(s):\n    return s[::-1]",
                "language": "python",
                "user_marked_final": True,
                "validation_status": "pending"
            }
        ],
        "design_tradeoffs": ["Chose slicing over loop for readability"],
        "scope_creep": [],
        "readme_notes": ["String utilities module needed"],
        "post_mvp_ideas": ["Add input validation"],
        "quality_flags": [],
        "summary": "Created simple string reversal function"
    }


@pytest.fixture
def mock_code_validation_response():
    """Mock response from AgentCore Code Interpreter"""
    return {
        "status": "valid",
        "details": "Function syntax is correct and will execute properly"
    }


class TestAriadneClew:
    """Test suite for AriadneClew agent class"""

    @pytest.mark.asyncio
    async def test_agent_processes_transcript_successfully(
        self, sample_chat_log, mock_agentcore_response, mock_code_validation_response
    ):
        """AriadneClew should process transcript and return structured recap"""

        with patch.object(AriadneClew, 'execute') as mock_execute, \
             patch.object(AriadneClew, '_persist_session_context') as mock_persist:

            # Mock the reasoning extraction
            mock_execute.side_effect = [
                json.dumps(mock_agentcore_response),  # First call: reasoning extraction
                mock_code_validation_response,        # Second call: code validation
            ]
            mock_persist.return_value = None

            agent = AriadneClew(session_id="test-session")
            result = await agent.process_transcript(sample_chat_log)

            # Verify structure
            assert "human_readable" in result
            assert "structured_data" in result
            assert "agent_metadata" in result
            assert result["session_id"] == "test-session"

            # Verify agent metadata shows AgentCore usage
            metadata = result["agent_metadata"]
            assert metadata["processed_by"] == "AriadneClew"
            assert metadata["code_snippets_validated"] == 1

            # Verify human readable contains key sections
            human_summary = result["human_readable"]
            assert "Session Recap" in human_summary
            assert "Key Insights" in human_summary
            assert "What You Built" in human_summary

    @pytest.mark.asyncio
    async def test_code_snippet_validation(
        self, mock_agentcore_response, mock_code_validation_response
    ):
        """AriadneClew should validate code snippets using AgentCore Code Interpreter"""

        with patch.object(AriadneClew, 'execute') as mock_execute:
            mock_execute.return_value = mock_code_validation_response

            agent = AriadneClew(session_id="test-validation")

            snippets = [
                {
                    "content": "def test(): return 'hello'",
                    "language": "python",
                    "user_marked_final": True,
                    "validation_status": "pending"
                }
            ]

            result = await agent._validate_code_snippets(snippets)

            assert len(result) == 1
            assert result[0]["validation_status"] == "valid"
            assert result[0]["validation_result"] == "Function syntax is correct and will execute properly"

            # Verify Code Interpreter was called with proper prompt
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args[0][0]
            assert "code_interpreter" in mock_execute.call_args[1]["tools"]
            assert "def test(): return 'hello'" in call_args

    @pytest.mark.asyncio
    async def test_conflict_resolution_multiple_finals(
        self, mock_agentcore_response
    ):
        """AriadneClew should autonomously resolve conflicts when multiple snippets marked final"""

        # Setup conflicting snippets
        conflicted_analysis = mock_agentcore_response.copy()
        conflicted_analysis["code_snippets"] = [
            {
                "content": "def reverse_v1(s): return s[::-1]",
                "language": "python",
                "user_marked_final": True,
                "validation_status": "valid"
            },
            {
                "content": "def reverse_v2(s): return ''.join(reversed(s))",
                "language": "python",
                "user_marked_final": True,
                "validation_status": "valid"
            }
        ]

        with patch.object(AriadneClew, 'execute') as mock_execute:
            mock_execute.return_value = {
                "chosen_index": 0,
                "reasoning": "Slicing approach is more Pythonic and efficient"
            }

            agent = AriadneClew(session_id="test-conflict")
            result = await agent._resolve_code_conflicts(conflicted_analysis)

            # Verify conflict resolution
            snippets = result["code_snippets"]
            assert snippets[0]["agent_chosen_final"] is True
            assert snippets[0]["resolution_reasoning"] == "Slicing approach is more Pythonic and efficient"
            assert snippets[1]["user_marked_final"] is False  # Downgraded

            # Verify quality flag was added
            assert len(result["quality_flags"]) > 0
            assert "Resolved conflict" in result["quality_flags"][0]

    @pytest.mark.asyncio
    async def test_memory_persistence(self, mock_agentcore_response):
        """AriadneClew should persist session context in AgentCore Memory"""

        with patch.object(AriadneClew, 'memory') as mock_memory:
            mock_memory.store = AsyncMock()

            agent = AriadneClew(session_id="test-memory")
            await agent._persist_session_context(mock_agentcore_response)

            # Verify memory was called with session data
            mock_memory.store.assert_called_once()
            call_args = mock_memory.store.call_args
            assert call_args[0][0] == "session_test-memory"

            stored_data = call_args[0][1]
            assert stored_data["session_id"] == "test-memory"
            assert "final_code_count" in stored_data
            assert "key_decisions" in stored_data

    @pytest.mark.asyncio
    async def test_memory_recall(self):
        """AriadneClew should recall previous session context from AgentCore Memory"""

        mock_previous_context = {
            "session_id": "test-recall",
            "final_code_count": 1,
            "key_decisions": ["Used iterative approach"],
            "session_summary": "Built fibonacci function"
        }

        with patch.object(AriadneClew, 'memory') as mock_memory:
            mock_memory.retrieve = AsyncMock(return_value=mock_previous_context)

            agent = AriadneClew(session_id="test-recall")
            result = await agent.recall_previous_session()

            assert result == mock_previous_context
            mock_memory.retrieve.assert_called_once_with("session_test-recall")

    @pytest.mark.asyncio
    async def test_empty_code_snippet_handling(self):
        """AriadneClew should handle empty code snippets gracefully"""

        agent = AriadneClew(session_id="test-empty")

        snippets = [
            {
                "content": "",
                "language": "python",
                "user_marked_final": False,
                "validation_status": "pending"
            }
        ]

        result = await agent._validate_code_snippets(snippets)

        assert len(result) == 1
        assert result[0]["validation_status"] == "empty"
        assert result[0]["validation_result"] == "No code content"

    @pytest.mark.asyncio
    async def test_invalid_input_handling(self):
        """AriadneClew should raise ValueError for invalid inputs"""

        agent = AriadneClew(session_id="test-invalid")

        # Test empty string
        with pytest.raises(ValueError, match="Invalid chat_log"):
            await agent.process_transcript("")

        # Test None input
        with pytest.raises(ValueError, match="Invalid chat_log"):
            await agent.process_transcript(None)

        # Test non-string input
        with pytest.raises(ValueError, match="Invalid chat_log"):
            await agent.process_transcript(123)

    @pytest.mark.asyncio
    async def test_json_parsing_error_handling(self, sample_chat_log):
        """AriadneClew should handle JSON parsing errors gracefully"""

        with patch.object(AriadneClew, 'execute') as mock_execute:
            # Return invalid JSON
            mock_execute.return_value = "invalid json response"

            agent = AriadneClew(session_id="test-json-error")

            with pytest.raises(ValueError, match="Agent returned invalid JSON"):
                await agent.process_transcript(sample_chat_log)

    @pytest.mark.asyncio
    async def test_agentcore_execution_error_handling(self, sample_chat_log):
        """AriadneClew should handle AgentCore execution errors gracefully"""

        with patch.object(AriadneClew, 'execute') as mock_execute:
            mock_execute.side_effect = Exception("AgentCore connection failed")

            agent = AriadneClew(session_id="test-execution-error")

            with pytest.raises(RuntimeError, match="Reasoning extraction failed"):
                await agent.process_transcript(sample_chat_log)


class TestBackwardsCompatibility:
    """Test backwards compatibility functions"""

    @pytest.mark.asyncio
    async def test_process_chat_log_function(
        self, sample_chat_log, mock_agentcore_response, mock_code_validation_response
    ):
        """process_chat_log() should work as drop-in replacement for old RecapAgent.run()"""

        with patch.object(AriadneClew, 'execute') as mock_execute, \
             patch.object(AriadneClew, '_persist_session_context') as mock_persist:

            mock_execute.side_effect = [
                json.dumps(mock_agentcore_response),
                mock_code_validation_response,
            ]
            mock_persist.return_value = None

            result = await process_chat_log(sample_chat_log, session_id="compat-test")

            # Should return same structure as AriadneClew.process_transcript()
            assert "human_readable" in result
            assert "structured_data" in result
            assert result["session_id"] == "compat-test"


class TestDemoFunction:
    """Test the demo functionality"""

    @pytest.mark.asyncio
    async def test_demo_runs_without_error(self):
        """Demo function should execute without raising exceptions"""

        # Mock all AgentCore interactions for demo
        with patch.object(AriadneClew, 'execute') as mock_execute, \
             patch.object(AriadneClew, '_persist_session_context') as mock_persist, \
             patch('builtins.print') as mock_print:  # Suppress print output

            mock_execute.side_effect = [
                json.dumps({
                    "session_id": "demo",
                    "aha_moments": ["Iterative approach is more efficient"],
                    "mvp_changes": ["Switched from recursive to iterative"],
                    "code_snippets": [
                        {
                            "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b",
                            "language": "python",
                            "user_marked_final": True,
                            "validation_status": "pending"
                        }
                    ],
                    "design_tradeoffs": ["Performance over simplicity"],
                    "scope_creep": [],
                    "readme_notes": [],
                    "post_mvp_ideas": [],
                    "quality_flags": [],
                    "summary": "Implemented efficient Fibonacci function"
                }),
                {"status": "valid", "details": "Function works correctly"}
            ]
            mock_persist.return_value = None

            # Import and run demo
            from agent import demo_ariadne_clew

            # Should not raise any exceptions
            await demo_ariadne_clew()

            # Verify demo printed output
            assert mock_print.call_count >= 2  # At least human readable + structured data


# Pytest configuration for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


class TestIntegration:
    """Integration tests that mock external dependencies but test full flow"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_pipeline_integration(self, sample_chat_log):
        """Test complete pipeline with realistic mocking"""

        # Mock all external dependencies
        with patch('agentcore.Agent.__init__') as mock_agent_init, \
             patch.object(AriadneClew, 'execute') as mock_execute, \
             patch.object(AriadneClew, 'memory') as mock_memory:

            # Setup mocks
            mock_agent_init.return_value = None
            mock_memory.store = AsyncMock()
            mock_memory.retrieve = AsyncMock(return_value=None)

            # Realistic agent responses
            mock_execute.side_effect = [
                json.dumps({
                    "session_id": "integration-test",
                    "aha_moments": ["String slicing is elegant"],
                    "mvp_changes": ["Added string utility"],
                    "code_snippets": [
                        {
                            "content": "def reverse_string(s):\n    return s[::-1]",
                            "language": "python",
                            "user_marked_final": True,
                            "validation_status": "pending"
                        }
                    ],
                    "design_tradeoffs": ["Simplicity over verbosity"],
                    "scope_creep": [],
                    "readme_notes": ["Document string utilities"],
                    "post_mvp_ideas": ["Add type hints"],
                    "quality_flags": [],
                    "summary": "Created string reversal utility"
                }),
                {"status": "valid", "details": "Clean, working function"}
            ]

            # Run full pipeline
            agent = AriadneClew(session_id="integration-test")
            result = await agent.process_transcript(sample_chat_log)

            # Verify complete output structure
            assert result["session_id"] == "integration-test"
            assert "human_readable" in result
            assert "structured_data" in result
            assert "agent_metadata" in result

            # Verify human readable formatting
            human_output = result["human_readable"]
            assert "Session Recap: integration-test" in human_output
            assert "Key Insights" in human_output
            assert "String slicing is elegant" in human_output
            assert "What You Built" in human_output
            assert "✅ Validated" in human_output

            # Verify agent metadata
            metadata = result["agent_metadata"]
            assert metadata["processed_by"] == "AriadneClew"
            assert metadata["code_snippets_validated"] == 1
            assert metadata["conflicts_resolved"] == 0

            # Verify memory was used
            mock_memory.store.assert_called_once()


if __name__ == "__main__":
    # Run tests with: python test_agent.py
    pytest.main([__file__, "-v"])
