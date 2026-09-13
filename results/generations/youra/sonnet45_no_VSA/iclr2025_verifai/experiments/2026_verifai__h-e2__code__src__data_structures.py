"""Core data structures for taxonomy construction."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict


class VerifierType(Enum):
    """Supported verification tools."""
    FRAMA_C = "frama-c"
    DAFNY = "dafny"
    WHY3 = "why3"


@dataclass
class ErrorCategory:
    """Single error category from a verifier."""
    verifier: str
    category_name: str
    description: str
    source: str  # "documentation" | "empirical"
    examples: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "category_name": self.category_name,
            "description": self.description,
            "source": self.source,
            "examples": self.examples
        }


@dataclass
class SemanticPrimitive:
    """Universal repair category."""
    primitive_id: str
    description: str
    proof_obligation_type: str
    keywords: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "primitive_id": self.primitive_id,
            "description": self.description,
            "proof_obligation_type": self.proof_obligation_type,
            "keywords": self.keywords,
            "examples": self.examples
        }


@dataclass
class Mapping:
    """Single verifier error → semantic primitive mapping."""
    verifier: str
    error_category: str
    semantic_primitive: Optional[str]
    confidence_score: float
    notes: str = ""

    def to_dict(self) -> Dict:
        return {
            "verifier": self.verifier,
            "error_category": self.error_category,
            "semantic_primitive": self.semantic_primitive,
            "confidence_score": self.confidence_score,
            "notes": self.notes
        }


@dataclass
class CoverageMetrics:
    """Coverage statistics for taxonomy validation."""
    aggregate_coverage: float
    per_verifier_coverage: Dict[str, float]
    unmapped_categories: Dict[str, List[str]]
    primitive_frequencies: Dict[str, int]
    gate_passed: bool
    threshold: float = 80.0

    def to_dict(self) -> Dict:
        return {
            "aggregate_coverage": self.aggregate_coverage,
            "per_verifier_coverage": self.per_verifier_coverage,
            "unmapped_categories": self.unmapped_categories,
            "primitive_frequencies": self.primitive_frequencies,
            "gate_passed": self.gate_passed,
            "threshold": self.threshold
        }
