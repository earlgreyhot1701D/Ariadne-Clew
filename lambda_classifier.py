# lambda_classifier.py

import re
import logging
from typing import List, Dict, Union

Block = Dict[str, str]

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MAX_CHARS = 100_000  # ~20k tokens max


def validate_input_length(text: str) -> None:
    """
    Ensures input is within safe token length for MVP.
    Raises ValueError if limit exceeded.
    """
    if len(text) > MAX_CHARS:
        raise ValueError(
            f"Input too long ({len(text)} chars). "
            f"Limit is {MAX_CHARS:,} characters (~20k tokens). "
            "Please trim or split your file before analysis."
        )


def classify_blocks(chat_log: Union[str, List[str]]) -> List[Block]:
    """
    Splits a chat log into blocks and classifies each as 'code' or 'text'.
    Code blocks are assumed to be delimited by triple backticks (```).

    Args:
        chat_log (str | list[str]): Raw chat content.

    Returns:
        list[dict]: List of {'type': 'code'|'text', 'content': str}

    Raises:
        ValueError: If input is not str/list[str] or if code fences are unbalanced.
    """
    if isinstance(chat_log, list):
        chat_log = "\n".join(chat_log)
    elif not isinstance(chat_log, str):
        raise ValueError("chat_log must be a string or list of strings")

    fence_count = chat_log.count("```")
    if fence_count % 2 != 0:
        logger.warning(f"Unmatched code fence in input. Found {fence_count} backticks.")
        raise ValueError(f"Unmatched code fence: found {fence_count} backticks.")

    # Regex split on ``` with optional language label and optional newline
    blocks = re.split(r"```(?:[a-zA-Z]*)?\n?", chat_log)

    result = []
    for idx, block in enumerate(blocks):
        content = block.strip()
        if not content:
            continue
        block_type = "code" if idx % 2 == 1 else "text"
        result.append({"type": block_type, "content": content})

    return result
