from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid


class RejectedVersion(BaseModel):
    code: str
    reason: str


class Recap(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    final: Optional[str] = None
    rejected_versions: List[RejectedVersion] = Field(default_factory=list)
    summary: str
    aha_moments: List[str] = Field(default_factory=list)
    quality_flags: List[str] = Field(default_factory=list)

    class Config:
        extra = "forbid"


def validate_recap_output(data: Dict[str, Any]) -> bool:
    """Basic schema validator for recap outputs (used in tests)."""
    required = {"session_id", "final", "rejected_versions", "summary", "aha_moments", "quality_flags"}
    for field in required:
        if field not in data:
            raise ValueError(f"Missing recap field: {field}")

    # final should be a string or None, not a dict
    if data["final"] is not None and not isinstance(data["final"], str):
        raise ValueError("Final snippet must be a string or None")

    if not isinstance(data["rejected_versions"], list):
        raise ValueError("Rejected must be a list")

    if not isinstance(data["summary"], str):
        raise ValueError("summary must be a string")

    return True
