"""
Agent wrapper for Ariadne Clew MVP.
Encapsulates guardrails + Bedrock classification + recap pipeline
into a single orchestrated Agent step.

MVP Roadmap compliance:
- AgentCore Code Interpreter enabled
- Guardrails attached to agent
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from lambda_classifier import validate_input_length
from backend.filters import enforce_size_limit, contains_deny_terms, scrub_pii
from backend.code_handler import validate_snippet
from backend.diffcheck import diff_code_blocks
from backend.recap_formatter import format_recap
from backend.memory_handler import store_recap
from backend.schema import Recap
from api_recap import classify_with_bedrock, load_prompts

logger = logging.getLogger(__name__)


class AgentConfig:
    """Lightweight config to control agent behavior."""

    def __init__(self, strict_guardrails: bool = True, persist_results: bool = True):
        self.strict_guardrails = strict_guardrails
        self.persist_results = persist_results


class RecapAgent:
    """Minimal agent wrapper to run a guarded recap pipeline."""

    def __init__(self, session_id: str = "default", config: Optional[AgentConfig] = None):
        self.session_id = session_id
        self.config = config or AgentConfig()

    def run(self, chat_log: str) -> Dict[str, Any]:
        """
        Run the full recap pipeline as an agent action.
        Returns a dict shaped according to Recap schema.
        Raises RuntimeError on persistence failure (if enabled).
        """
        if not chat_log or not isinstance(chat_log, str):
            raise ValueError("Invalid or missing 'chat_log' (must be a non-empty string).")

        # --- Guardrails ---
        validate_input_length(chat_log)
        enforce_size_limit(chat_log)

        if contains_deny_terms(chat_log):
            if self.config.strict_guardrails:
                raise ValueError("Input contains unsafe terms.")
            else:
                logger.warning("Unsafe terms detected but strict_guardrails=False, continuing.")
        scrubbed_log = scrub_pii(chat_log)

        # --- Classification (Bedrock) ---
        full_prompt = f"{load_prompts()}\n\n{scrubbed_log}"
        blocks = classify_with_bedrock(full_prompt)

        # --- Validation ---
        validated_blocks: List[Dict[str, Any]] = []
        for block in blocks:
            if block.get("type") == "code":
                result = validate_snippet(block.get("content", ""))
                block["validation"] = result
            validated_blocks.append(block)

        # --- Diff & recap ---
        recap_dict: Dict[str, Any] = diff_code_blocks(validated_blocks)
        recap_model: Recap = Recap.model_validate(recap_dict)
        recap_payload: Dict[str, Any] = format_recap(recap_model)

        # --- Persistence ---
        if self.config.persist_results:
            success = store_recap("last_recap", recap_payload, session_id=self.session_id)
            if not success:
                logger.error("Failed to persist recap for session %s", self.session_id)
                raise RuntimeError("Unable to persist recap; please retry.")

        logger.info("RecapAgent completed successfully for session %s", self.session_id)
        return recap_payload
