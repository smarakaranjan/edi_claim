from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ElementDef:
    id: str
    required: bool = False
    allowed: Optional[List[str]] = None


@dataclass
class SegmentDef:
    id: str
    elements: Dict[int, ElementDef]
    max_repeat: int = 1


@dataclass
class LoopDef:
    id: str
    segments: Dict[str, SegmentDef]
    child_loops: Dict[str, "LoopDef"] = field(default_factory=dict)
