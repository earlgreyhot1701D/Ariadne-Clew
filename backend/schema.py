from pydantic import BaseModel, Field
from typing import List, Optional
import uuid

class RejectedVersion(BaseModel):
    code: str
    reason: str

class Recap(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    final: Optional[str] = None
    rejected_versions: List[RejectedVersion] = []
    summary: str
    aha_moments: List[str] = []
    quality_flags: List[str] = []

    class Config:
        extra = "forbid"
