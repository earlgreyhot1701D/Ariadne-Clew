"""
Input filtering and validation for Ariadne Clew.
Implements content safety guardrails.
"""

import re

# Dangerous command substrings to block (simple substring checks)
DANGEROUS_COMMANDS = {
    # File system operations
    "rm -rf", "rm -r", "rmdir", "del /s", "rd /s",
    # Network operations
    "wget", "curl", "nc ", "netcat", "telnet",
    # System operations
    "sudo ", "su ", "chmod 777", "chown",
    # Script execution
    "eval(", "exec(", "system(", "shell_exec",
    # Database operations
    "drop table", "drop database", "truncate",
    # Process operations
    "kill -9", "killall", "pkill",
    # Explicit hackathon guardrails
    "begin rsa private key",
}

# Regex patterns for complex cases
DANGEROUS_PATTERNS = [
    r"rm\s+-r[f]?\s*/",              # rm -rf /
    r">\s*/dev/(null|zero)",         # redirect to system devices
    r":\$\{\s*:\|:&\s*\};:",         # fork bomb
    r"__import__\s*\(",              # dynamic import
]


def contains_deny_terms(text: str) -> bool:
    """
    Check if input contains dangerous commands or patterns.
    Case-insensitive, catches both substrings and regex hits.
    """
    if not text:
        return False

    normalized_text = text.lower()

    # Substring checks
    for term in DANGEROUS_COMMANDS:
        if term.lower() in normalized_text:
            return True

    # Regex checks
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, normalized_text, re.IGNORECASE):
            return True

    return False


def enforce_size_limit(text: str, max_size: int = 100_000) -> None:
    """
    Enforce maximum input size in characters.
    Raises ValueError if exceeded.
    """
    if len(text) > max_size:
        raise ValueError(f"Input size {len(text)} exceeds limit of {max_size} characters")


def scrub_pii(text: str) -> str:
    """
    Scrub common PII from text: emails, phone numbers, SSNs, credit cards.
    """
    if not text:
        return text

    # Email
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[EMAIL_REDACTED]", text)

    # Phone (US style)
    text = re.sub(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE_REDACTED]", text)

    # SSN
    text = re.sub(r"\b\d{3}-?\d{2}-?\d{4}\b", "[SSN_REDACTED]", text)

    # Credit card (naive 16-digit sequence)
    text = re.sub(r"\b\d{16}\b", "[CC_REDACTED]", text)

    return text
