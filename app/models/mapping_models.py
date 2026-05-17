from pydantic import BaseModel
from typing import Optional


class MappingSuggestion(BaseModel):
    source: str
    target: str
    confidence: str


class MappingRequest(BaseModel):
    source_schema_id: int
    target_schema_id: int
    notes: Optional[str] = None