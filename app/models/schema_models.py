from pydantic import BaseModel, Field
from typing import List, Optional


class Pin(BaseModel):
    name: str
    dir: str
    type: str = "unknown"
    mandatory: bool = False
    description: Optional[str] = None


class Parameter(BaseModel):
    name: str
    type: str = "unknown"
    default: Optional[str] = None
    mandatory: bool = False
    description: Optional[str] = None


class BlockSchema(BaseModel):
    vendor: str
    block_name: str
    block_type: str
    version: str
    description: Optional[str] = None
    pins: List[Pin] = Field(default_factory=list)
    parameters: List[Parameter] = Field(default_factory=list)
    notes: Optional[str] = None
