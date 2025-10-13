"""
Ariadne Clew: AWS AgentCore-powered reasoning agent.
Uses the real AWS AgentCore Runtime API with BedrockAgentCoreApp.

Built for AWS Agent Hackathon - demonstrates AgentCore integration
with reasoning extraction and structured recap generation.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

# Real AWS AgentCore imports
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

# Keep your existing logic
from backend.schema import Recap
from backend.recap_formatter import format_recap

logger = logging.getLogger(__name__)

# Initialize AWS AgentCore app and agent
app = BedrockAgentCoreApp()
agent = Agent()


class AriadneClew:
    """
    AWS AgentCore-powered reasoning agent using the real BedrockAgentCoreApp.

    Transforms chaotic chat transcripts into structured reasoning artifacts
    using AWS AgentCore Runtime and Strands agents.
    """

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.app = app
        self.agent = agent

    async def process_transcript(self, chat_log: str) -> Dict[str, Any]:
        """
        Process chat transcript using AWS AgentCore (async version)

        This uses the real AgentCore runtime to:
        1. Extract reasoning from transcript
        2. Structure the response
        3. Return human-readable recap
        """

        if not chat_log or not isinstance(chat_log, str):
            raise ValueError("Invalid chat_log: must be non-empty string")

        logger.info(f"AriadneClew processing transcript for session {self.session_id}")

        try:
            # Use the real AgentCore agent for reasoning extraction
            reasoning_prompt = self._build_reasoning_prompt(chat_log)

            # This calls the actual AgentCore/Bedrock integration
            result = self.agent(reasoning_prompt)

            # Handle different response formats from strands.Agent
            analysis = self._extract_analysis_from_result(result)
            analysis["session_id"] = self.session_id

            # Format for demo
            recap = self._format_for_demo(analysis)

            logger.info(f"AriadneClew completed processing for session {self.session_id}")
            return recap

        except Exception as e:
            logger.error(f"AriadneClew processing failed: {e}")
            raise RuntimeError(f"Reasoning extraction failed: {str(e)}")

    def _process_transcript_sync(self, chat_log: str) -> Dict[str, Any]:
        """
        Synchronous version for AgentCore entrypoint

        Same logic as async version but without await keywords
        """
        if not chat_log or not isinstance(chat_log, str):
            raise ValueError("Invalid chat_log: must be non-empty string")

        logger.info(f"AriadneClew processing transcript for session {self.session_id}")

        try:
            reasoning_prompt = self._build_reasoning_prompt(chat_log)
            result = self.agent(reasoning_prompt)

            # Log what we actually received for debugging
            logger.info(f"Strands agent returned type: {type(result)}")
            logger.info(f"Strands agent returned: {str(result)[:200]}...")

            # Handle different response formats from strands.Agent
            analysis = self._extract_analysis_from_result(result)
            analysis["session_id"] = self.session_id
            recap = self._format_for_demo(analysis)

            logger.info(f"AriadneClew completed processing for session {self.session_id}")
            return recap

        except Exception as e:
            logger.error(f"AriadneClew processing failed: {e}")
            raise RuntimeError(f"Reasoning extraction failed: {str(e)}")

    def _extract_analysis_from_result(self, result) -> Dict[str, Any]:
        """
        Extract structured analysis from strands.Agent result

        Handles different possible return formats from the agent
        """
        try:
            # Case 1: Strands Agent format with content array (MOST COMMON)
            # Returns: {"role": "assistant", "content": [{"text": "```json\n{...}\n```"}], "session_id": "..."}
            if isinstance(result, dict) and "content" in result:
                content = result.get("content", [])
                if isinstance(content, list) and len(content) > 0:
                    text = content[0].get("text", "")
                    if text:
                        logger.info("✓ Extracting from Strands Agent content array format")
                        return self._parse_agent_response(text)

            # Case 2: Result has a message attribute (string)
            elif hasattr(result, 'message'):
                response_text = result.message
                return self._parse_agent_response(response_text)

            # Case 3: Result is already a dict with the data we need
            elif isinstance(result, dict):
                # If it looks like our expected structure, use it directly
                if "aha_moments" in result or "code_snippets" in result:
                    return result

                # If it has a message key, parse that
                elif "message" in result:
                    return self._parse_agent_response(result["message"])

                # If it's some other dict, try to convert to string and parse
                else:
                    return self._parse_agent_response(str(result))

            # Case 4: Result is a string response
            elif isinstance(result, str):
                return self._parse_agent_response(result)

            # Case 5: Unknown format - convert to string and try to parse
            else:
                logger.warning(f"Unknown result format: {type(result)}, converting to string")
                return self._parse_agent_response(str(result))

        except Exception as e:
            logger.error(f"Failed to extract analysis from result: {e}")
            logger.error(f"Result was: {result}")

            # Return a minimal valid structure so the agent doesn't crash completely
            return {
                "session_id": self.session_id,
                "aha_moments": ["Error processing agent response"],
                "mvp_changes": [],
                "code_snippets": [],
                "design_tradeoffs": [],
                "scope_creep": [],
                "readme_notes": [],
                "post_mvp_ideas": [],
                "quality_flags": [f"Agent response parsing failed: {str(e)}"],
                "summary": "Unable to process agent response properly"
            }

    def _build_reasoning_prompt(self, chat_log: str) -> str:
        """Build the reasoning extraction prompt for AgentCore"""
        return f"""
        You are Ariadne Clew, a reasoning preservation agent for AI-native builders.

        Analyze this chat transcript and extract structured insights:

        1. **Aha moments**: Key insights or discoveries
        2. **MVP changes**: Scope edits, pivots, feature decisions
        3. **Code snippets**: All code blocks with language and context
        4. **Design tradeoffs**: Explicit rationale for choices
        5. **Scope creep**: Evidence of expanding beyond MVP
        6. **README notes**: Facts that belong in documentation
        7. **Post-MVP ideas**: Features deferred for later
        8. **Quality assessment**: Session structure evaluation

        Return valid JSON with this structure:
        {{
          "session_id": "{self.session_id}",
          "aha_moments": ["insight 1", "insight 2"],
          "mvp_changes": ["change 1", "change 2"],
          "code_snippets": [
            {{
              "content": "actual code here",
              "language": "python|javascript|etc",
              "user_marked_final": true|false,
              "context": "why this code was written"
            }}
          ],
          "design_tradeoffs": ["tradeoff 1", "tradeoff 2"],
          "scope_creep": ["creep 1", "creep 2"],
          "readme_notes": ["note 1", "note 2"],
          "post_mvp_ideas": ["idea 1", "idea 2"],
          "quality_flags": ["flag 1", "flag 2"],
          "summary": "One paragraph session summary"
        }}

        Chat transcript:
        {chat_log}

        Return ONLY valid JSON. Empty arrays [] if no items found.
        """

    def _parse_agent_response(self, response: str) -> Dict[str, Any]:
        """Parse the agent response into structured data"""
        try:
            # Handle case where response might already be a dict converted to string
            if isinstance(response, dict):
                return response

            # Convert to string if it isn't already
            response_str = str(response)

            # Try to parse as JSON
            if response_str.strip().startswith('{') and response_str.strip().endswith('}'):
                return json.loads(response_str)

            # Try to extract JSON from markdown code blocks
            if '```json' in response_str:
                start = response_str.find('```json') + 7
                end = response_str.find('```', start)
                if end != -1:
                    json_str = response_str[start:end].strip()
                    return json.loads(json_str)

            # Try to extract JSON from any code block
            if '```' in response_str:
                start = response_str.find('```') + 3
                end = response_str.find('```', start)
                if end != -1:
                    json_str = response_str[start:end].strip()
                    # Skip language identifier if present
                    if json_str.startswith('json\n'):
                        json_str = json_str[5:]
                    return json.loads(json_str)

            # Fallback: try to find JSON anywhere in response
            start = response_str.find('{')
            end = response_str.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response_str[start:end]
                return json.loads(json_str)

            raise ValueError("No valid JSON found in agent response")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent response as JSON: {e}")
            logger.error(f"Agent response was: {response}")
            raise ValueError(f"Agent returned invalid JSON: {str(e)}")

    def _format_for_demo(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Format the analysis for demo output"""

        # Generate human-readable summary
        human_readable = self._generate_human_summary(analysis)

        # Try to validate with your existing schema
        try:
            # Create a compatible version for your existing schema
            schema_compatible = {
                "session_id": analysis.get("session_id"),
                "summary": analysis.get("summary", ""),
                "final": analysis.get("code_snippets", []),
                "rejected_versions": [],  # Not used in new format
                "aha_moments": analysis.get("aha_moments", []),
                "scope_creep": analysis.get("scope_creep", [])
            }

            recap_model = Recap.model_validate(schema_compatible)
            structured_data = format_recap(recap_model)
        except Exception as e:
            logger.warning(f"Schema validation failed: {e}")
            # Fallback - use analysis as-is
            structured_data = analysis

        return {
            "human_readable": human_readable,
            "structured_data": structured_data,
            "session_id": self.session_id,
            "agent_metadata": {
                "processed_by": "AriadneClew",
                "agentcore_runtime": "BedrockAgentCoreApp",
                "strands_agent": True,
                "code_snippets_found": len(analysis.get("code_snippets", [])),
                "insights_extracted": len(analysis.get("aha_moments", []))
            }
        }

    def _generate_human_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate scannable human-readable recap"""

        summary_parts = []

        # Session overview
        summary_parts.append(f"## Session Recap: {analysis.get('session_id', 'Unknown')}")
        summary_parts.append("")

        if analysis.get("summary"):
            summary_parts.append(f"**Overview:** {analysis['summary']}")
            summary_parts.append("")

        # Key insights
        if analysis.get("aha_moments"):
            summary_parts.append("### Key Insights")
            for moment in analysis["aha_moments"]:
                summary_parts.append(f"- {moment}")
            summary_parts.append("")

        # Code found
        if analysis.get("code_snippets"):
            summary_parts.append("### Code Discovered")
            for snippet in analysis["code_snippets"]:
                lang = snippet.get("language", "code")
                final_marker = "FINAL" if snippet.get("user_marked_final") else ""
                summary_parts.append(f"**{lang} snippet** {final_marker}")
                if snippet.get("context"):
                    summary_parts.append(f"*Context*: {snippet['context']}")
            summary_parts.append("")

        # MVP changes
        if analysis.get("mvp_changes"):
            summary_parts.append("### Scope Changes")
            for change in analysis["mvp_changes"]:
                summary_parts.append(f"- {change}")
            summary_parts.append("")

        # Design decisions
        if analysis.get("design_tradeoffs"):
            summary_parts.append("### Design Decisions")
            for tradeoff in analysis["design_tradeoffs"]:
                summary_parts.append(f"- {tradeoff}")
            summary_parts.append("")

        # Post-MVP ideas
        if analysis.get("post_mvp_ideas"):
            summary_parts.append("### Post-MVP Ideas")
            for idea in analysis["post_mvp_ideas"]:
                summary_parts.append(f"- {idea}")
            summary_parts.append("")

        return "\n".join(summary_parts)


# AgentCore entrypoint - this is how AgentCore calls your agent
@app.entrypoint
def invoke(payload):
    """
    AWS AgentCore entrypoint for Ariadne Clew.

    Handles multiple payload formats for debugging.
    """
    try:
        # Debug logging to see what AgentCore is sending
        logger.info(f"Received payload: {payload}")

        # Try different payload formats that AgentCore might send
        chat_log = payload.get("chat_log") or payload.get("prompt") or payload.get("message")
        session_id = payload.get("session_id", "agentcore-session")

        if not chat_log:
            error_msg = f"Missing chat content in payload. Received keys: {list(payload.keys())}. Full payload: {payload}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "status": "failed"
            }

        # Create AriadneClew instance and process
        ariadne = AriadneClew(session_id=session_id)

        # Use sync version for AgentCore entrypoint
        result = ariadne._process_transcript_sync(chat_log)

        return {
            "status": "success",
            "result": result
        }

    except Exception as e:
        error_msg = f"AgentCore entrypoint failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "status": "failed",
            "error": error_msg
        }


# Backwards compatibility function
async def process_chat_log(chat_log: str, session_id: str = "default") -> Dict[str, Any]:
    """Backwards compatible entry point"""
    ariadne = AriadneClew(session_id=session_id)
    return await ariadne.process_transcript(chat_log)


# Demo function
async def demo_ariadne_clew():
    """Demo AriadneClew with sample transcript"""
    sample_transcript = """
    User: I need a function to calculate fibonacci numbers for my project

    Assistant: Here's a recursive approach:

    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)

    User: Actually, that might be slow for large numbers. Can we do iterative?

    Assistant: Good point! Here's an iterative version:

    def fibonacci(n):
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b

    User: Perfect, let's go with the iterative version as final.
    """

    ariadne = AriadneClew(session_id="demo")
    result = await ariadne.process_transcript(sample_transcript)

    print("=== HUMAN READABLE ===")
    print(result["human_readable"])
    print("\n=== STRUCTURED DATA ===")
    print(json.dumps(result["structured_data"], indent=2))
    print("\n=== AGENT METADATA ===")
    print(json.dumps(result["agent_metadata"], indent=2))


# For local testing with AgentCore
if __name__ == "__main__":
    print("Starting Ariadne Clew AgentCore app...")
    print("Test with: curl -X POST http://localhost:8080/invocations -H 'Content-Type: application/json' -d '{\"chat_log\": \"User: Hello\\nAssistant: Hi there!\"}'")
    app.run()
