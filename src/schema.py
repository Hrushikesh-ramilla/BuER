"""Data models and schemas for Business Entity Resolution pipeline."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass(slots=True)
class BusinessRecord:
    """Represents a single business entity record from any source."""
    entity_id: str
    business_name: str
    business_address: str
    country: str
    source_id: int
    normalized_name: str = ""
    normalized_address: str = ""
    core_name_tokens: Set[str] = field(default_factory=set)
    address_tokens: Set[str] = field(default_factory=set)
    house_number: Optional[str] = None
    postal_code: Optional[str] = None


@dataclass(slots=True)
class CandidateMatch:
    """Represents a scored candidate match between S1 and pool record."""
    source_id: str
    target_id: str
    match_probability: float = 0.0
    ranking_score: float = 0.0
    features: Optional[List[float]] = None


@dataclass(slots=True)
class PipelineMetrics:
    """Holds precision, recall, and Macro F0.5 metrics."""
    macro_f05: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    total_entities: int = 0
    total_links: int = 0
    singletons: int = 0
