from pydantic import BaseModel, Field
from typing import List, Optional
import uuid


class EnrichedSnippet(BaseModel):
    version: int
    snippet_id: str
    content: str
    diff_summary: str


class Recap(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    final: EnrichedSnippet
    rejected: List[EnrichedSnippet] = Field(default_factory=list)
    text_summary: str

    # Optional extras
    aha_moments: List[str] = Field(default_factory=list)
    quality_flags: List[str] = Field(default_factory=list)

    class Config:
        extra = "forbid"
