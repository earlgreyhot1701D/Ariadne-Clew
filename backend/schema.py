# backend/schema.py
import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class EnrichedSnippet(BaseModel):
    """
    Represents a validated code snippet with optional diff and validation metadata.
    """

    version: int
    snippet_id: str
    content: str
    diff_summary: str = "No change"
    validation: Dict[str, Any] = Field(default_factory=dict)


class Recap(BaseModel):
    """
    Canonical recap model that aligns schema, frontend, and tests.
    """

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    final: Optional[EnrichedSnippet] = None
    rejected_versions: List[EnrichedSnippet] = Field(default_factory=list)
    summary: str = Field(default="")
    aha_moments: List[str] = Field(default_factory=list)
    quality_flags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid", populate_by_name=True)
