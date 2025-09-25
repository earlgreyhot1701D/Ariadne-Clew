"""
Ariadne Clew: AWS AgentCore-powered reasoning agent.
Preserves builder context from chaotic chat transcripts into structured clarity.

Built for AWS Agent Hackathon - demonstrates autonomous agent behavior
with AgentCore Code Interpreter, Memory, and Bedrock integration.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import json
import asyncio

# AgentCore imports - the hero of our story
from agentcore import Agent
from agentcore.tools import CodeInterpreter
from agentcore.memory import Memory
from agentcore.guardrails import ContentFilter, PIIFilter

# Keep minimal custom logic for demo polish
from backend.schema import Recap
from backend.recap_formatter import format_recap

logger = logging.getLogger(__name__)


class AriadneClew(Agent):
    """
    AWS AgentCore-powered reasoning agent that transforms chaotic chat transcripts
    into structured reasoning artifacts.

    Demonstrates true agentic behavior:
    - Autonomous content classification
    - Secure code validation via AgentCore Code Interpreter
    - Cross-session memory persistence via AgentCore Memory
    - Built-in guardrails for production safety
    """

    def __init__(self, session_id: str = "default"):
        """Initialize Ariadne Clew with full AgentCore stack"""

        # Configure AgentCore as the foundation
        super().__init__(
            model_provider="bedrock",
            model="claude-sonnet-3-5",
            tools=[CodeInterpreter()],
            memory=Memory(),
            guardrails=[
                ContentFilter(
                    deny_terms=["password", "api_key", "rm -rf /", "BEGIN RSA PRIVATE KEY"]
                ),
                PIIFilter(scrub_emails=True, scrub_phones=True)
            ],
            max_tokens=4000
        )

        self.session_id = session_id
        self._reasoning_prompt = self._load_reasoning_prompt()

    def _load_reasoning_prompt(self) -> str:
        """Load the core reasoning extraction prompt - the agent's brain"""
        return """
        You are Ariadne Clew, a reasoning preservation agent for AI-native builders.

        Your mission: Transform chaotic chat transcripts into structured clarity.

        Analyze the provided chat transcript and extract these elements:

        1. **Aha moments**: Key insights, discoveries, or shifts in understanding
        2. **MVP changes**: Scope edits, pivots, feature commitments or cuts
        3. **Code snippets**: All code blocks (you'll validate these separately)
        4. **Design tradeoffs**: Explicit rationale for choosing approach X over Y
        5. **Scope creep**: Evidence of expanding beyond stated MVP
        6. **README notes**: Facts or concepts that belong in documentation
        7. **Post-MVP ideas**: Features explicitly deferred for later
        8. **Quality assessment**: Overall session structure and clarity

        For each code snippet you find:
        - Extract the exact code content
        - Note the programming language
        - Mark if user called it "final" or "preferred"
        - You'll validate functionality using code interpreter

        Return structured JSON following this schema:
        {
          "session_id": "string",
          "aha_moments": ["insight 1", "insight 2"],
          "mvp_changes": ["change 1", "change 2"],
          "code_snippets": [
            {
              "content": "actual code here",
              "language": "python|javascript|etc",
              "user_marked_final": true|false,
              "validation_status": "pending"
            }
          ],
          "design_tradeoffs": ["tradeoff 1", "tradeoff 2"],
          "scope_creep": ["creep 1", "creep 2"],
          "readme_notes": ["note 1", "note 2"],
          "post_mvp_ideas": ["idea 1", "idea 2"],
          "quality_flags": ["flag 1", "flag 2"],
          "summary": "One paragraph summary of the session"
        }

        CRITICAL: Return ONLY valid JSON. No markdown, no explanations, just JSON.
        If any category has no items, use empty array [].
        Never hallucinate - if unclear, leave empty rather than guess.
        """

    async def process_transcript(self, chat_log: str) -> Dict[str, Any]:
        """
        Main entry point: Process chat transcript into structured recap

        This demonstrates autonomous agent behavior:
        1. Analyzes content and extracts reasoning
        2. Validates code snippets securely
        3. Resolves conflicts between versions
        4. Persists decisions in memory
        5. Returns human-readable recap
        """

        if not chat_log or not isinstance(chat_log, str):
            raise ValueError("Invalid chat_log: must be non-empty string")

        logger.info(f"AriadneClew processing transcript for session {self.session_id}")

        try:
            # Step 1: Let AgentCore handle reasoning extraction
            reasoning_task = f"{self._reasoning_prompt}\n\nCHAT TRANSCRIPT:\n{chat_log}"
            raw_analysis = await self.execute(reasoning_task)

            # Parse the structured response
            if isinstance(raw_analysis, str):
                analysis = json.loads(raw_analysis)
            else:
                analysis = raw_analysis

            analysis["session_id"] = self.session_id

            # Step 2: Validate code snippets with AgentCore Code Interpreter
            validated_snippets = await self._validate_code_snippets(
                analysis.get("code_snippets", [])
            )
            analysis["code_snippets"] = validated_snippets

            # Step 3: Resolve conflicts and determine "final" versions
            analysis = await self._resolve_code_conflicts(analysis)

            # Step 4: Store reasoning in AgentCore Memory for continuity
            await self._persist_session_context(analysis)

            # Step 5: Format for human consumption
            recap = await self._format_for_demo(analysis)

            logger.info(f"AriadneClew completed processing for session {self.session_id}")
            return recap

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent response as JSON: {e}")
            raise ValueError("Agent returned invalid JSON - please retry")

        except Exception as e:
            logger.error(f"AriadneClew processing failed: {e}")
            raise RuntimeError(f"Reasoning extraction failed: {str(e)}")

    async def _validate_code_snippets(self, snippets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use AgentCore Code Interpreter to validate code snippets"""

        validated = []

        for snippet in snippets:
            code_content = snippet.get("content", "")
            language = snippet.get("language", "unknown")

            if not code_content.strip():
                snippet["validation_status"] = "empty"
                snippet["validation_result"] = "No code content"
                validated.append(snippet)
                continue

            try:
                # Use AgentCore Code Interpreter for secure validation
                validation_prompt = f"""
                Validate this {language} code snippet:

                ```{language}
                {code_content}
                ```

                Check for:
                1. Syntax validity
                2. Basic functionality
                3. Potential runtime errors
                4. Security concerns

                Return: {{"status": "valid|invalid|warning", "details": "explanation"}}
                """

                result = await self.execute(validation_prompt, tools=["code_interpreter"])

                if isinstance(result, str):
                    validation_data = json.loads(result)
                else:
                    validation_data = result

                snippet["validation_status"] = validation_data.get("status", "unknown")
                snippet["validation_result"] = validation_data.get("details", "No details")

            except Exception as e:
                logger.warning(f"Code validation failed for snippet: {e}")
                snippet["validation_status"] = "error"
                snippet["validation_result"] = f"Validation error: {str(e)}"

            validated.append(snippet)

        return validated

    async def _resolve_code_conflicts(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Autonomous conflict resolution when multiple 'final' versions exist"""

        snippets = analysis.get("code_snippets", [])
        final_snippets = [s for s in snippets if s.get("user_marked_final", False)]

        if len(final_snippets) > 1:
            # Let the agent decide which version to prefer
            conflict_prompt = f"""
            Multiple code snippets marked as 'final'. Analyze and choose the best version:

            {json.dumps(final_snippets, indent=2)}

            Consider:
            - Validation status (prefer valid over invalid)
            - Code quality and completeness
            - Position in transcript (later often better)

            Return: {{"chosen_index": 0, "reasoning": "why this version"}}
            """

            try:
                resolution = await self.execute(conflict_prompt)
                if isinstance(resolution, str):
                    resolution_data = json.loads(resolution)
                else:
                    resolution_data = resolution

                chosen_idx = resolution_data.get("chosen_index", 0)
                reasoning = resolution_data.get("reasoning", "Agent preference")

                # Mark the chosen snippet and add resolution metadata
                for i, snippet in enumerate(final_snippets):
                    if i == chosen_idx:
                        snippet["agent_chosen_final"] = True
                        snippet["resolution_reasoning"] = reasoning
                    else:
                        snippet["user_marked_final"] = False  # Downgrade others

                # Add to quality flags
                analysis["quality_flags"] = analysis.get("quality_flags", [])
                analysis["quality_flags"].append(
                    f"Resolved conflict: {len(final_snippets)} versions marked final, "
                    f"chose version based on: {reasoning}"
                )

            except Exception as e:
                logger.warning(f"Conflict resolution failed: {e}")
                # Fallback: prefer last marked final
                for snippet in final_snippets[:-1]:
                    snippet["user_marked_final"] = False

        return analysis

    async def _persist_session_context(self, analysis: Dict[str, Any]) -> None:
        """Store key decisions in AgentCore Memory for cross-session continuity"""

        try:
            # Store the final code decision for future reference
            final_snippets = [
                s for s in analysis.get("code_snippets", [])
                if s.get("user_marked_final", False) or s.get("agent_chosen_final", False)
            ]

            memory_context = {
                "session_id": self.session_id,
                "timestamp": "2025-09-25",  # Would use datetime in production
                "final_code_count": len(final_snippets),
                "key_decisions": analysis.get("mvp_changes", [])[:3],  # Store top 3
                "session_summary": analysis.get("summary", "")
            }

            await self.memory.store(f"session_{self.session_id}", memory_context)
            logger.info(f"Persisted session context for {self.session_id}")

        except Exception as e:
            logger.warning(f"Memory persistence failed: {e}")
            # Don't fail the whole pipeline for memory issues

    async def _format_for_demo(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Format the structured analysis into demo-ready output"""

        # Create human-readable summary
        human_readable = self._generate_human_summary(analysis)

        # Validate against schema (keeping your existing validation)
        try:
            recap_model = Recap.model_validate(analysis)
            formatted_recap = format_recap(recap_model)
        except Exception as e:
            logger.warning(f"Schema validation failed: {e}")
            # Fallback formatting
            formatted_recap = analysis

        return {
            "human_readable": human_readable,
            "structured_data": formatted_recap,
            "session_id": self.session_id,
            "agent_metadata": {
                "processed_by": "AriadneClew",
                "agentcore_version": "1.0",
                "code_snippets_validated": len(analysis.get("code_snippets", [])),
                "conflicts_resolved": len([
                    s for s in analysis.get("code_snippets", [])
                    if s.get("agent_chosen_final", False)
                ])
            }
        }

    def _generate_human_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate scannable human-readable recap"""

        snippets = analysis.get("code_snippets", [])
        final_snippets = [s for s in snippets if
                         s.get("user_marked_final", False) or s.get("agent_chosen_final", False)]

        summary_parts = []

        # Session overview
        summary_parts.append(f"## Session Recap: {analysis.get('session_id', 'Unknown')}")
        summary_parts.append("")

        if analysis.get("summary"):
            summary_parts.append(f"**Overview:** {analysis['summary']}")
            summary_parts.append("")

        # Key insights
        if analysis.get("aha_moments"):
            summary_parts.append("### 💡 Key Insights")
            for moment in analysis["aha_moments"]:
                summary_parts.append(f"- {moment}")
            summary_parts.append("")

        # Final code
        if final_snippets:
            summary_parts.append("### 🎯 What You Built")
            for snippet in final_snippets:
                status = "✅" if snippet.get("validation_status") == "valid" else "⚠️"
                lang = snippet.get("language", "code")
                summary_parts.append(f"**Final {lang}**: {status} Validated")
                if snippet.get("resolution_reasoning"):
                    summary_parts.append(f"*Why this version*: {snippet['resolution_reasoning']}")
            summary_parts.append("")

        # MVP changes
        if analysis.get("mvp_changes"):
            summary_parts.append("### 🔄 Scope Changes")
            for change in analysis["mvp_changes"]:
                summary_parts.append(f"- {change}")
            summary_parts.append("")

        # Post-MVP ideas
        if analysis.get("post_mvp_ideas"):
            summary_parts.append("### 🚀 Post-MVP Ideas")
            for idea in analysis["post_mvp_ideas"]:
                summary_parts.append(f"- {idea}")
            summary_parts.append("")

        return "\n".join(summary_parts)

    async def recall_previous_session(self) -> Optional[Dict[str, Any]]:
        """Demonstrate AgentCore Memory - recall previous decisions"""

        try:
            previous_context = await self.memory.retrieve(f"session_{self.session_id}")
            return previous_context
        except Exception as e:
            logger.warning(f"Memory recall failed: {e}")
            return None


# Convenience function for backwards compatibility
async def process_chat_log(chat_log: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Backwards-compatible entry point for existing code.
    Creates AriadneClew instance and processes transcript.
    """

    agent = AriadneClew(session_id=session_id)
    return await agent.process_transcript(chat_log)


# Demo/test helper
async def demo_ariadne_clew():
    """Quick demo of AriadneClew capabilities"""

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

    agent = AriadneClew(session_id="demo")
    result = await agent.process_transcript(sample_transcript)

    print("=== HUMAN READABLE ===")
    print(result["human_readable"])
    print("\n=== STRUCTURED DATA ===")
    print(json.dumps(result["structured_data"], indent=2))


if __name__ == "__main__":
    # For local testing
    asyncio.run(demo_ariadne_clew())
