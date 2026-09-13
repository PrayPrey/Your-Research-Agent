"""Semantic primitive identification through keyword-based clustering."""

from typing import List, Dict
from ..data_structures import ErrorCategory, SemanticPrimitive


class SemanticClusterer:
    """Identify universal semantic primitives from error categories."""

    def __init__(self, primitives_seed: List[str]):
        """Initialize with candidate primitive list."""
        self.primitives_seed = primitives_seed
        self.primitive_definitions = self._define_primitives()

    def _define_primitives(self) -> List[SemanticPrimitive]:
        """Define semantic primitives with keywords and proof obligation types."""
        return [
            SemanticPrimitive(
                primitive_id="MISSING_PRECONDITION",
                description="Function precondition not satisfied at call site",
                proof_obligation_type="precondition",
                keywords=["precondition", "requires", "pre", "caller"],
                examples=[]
            ),
            SemanticPrimitive(
                primitive_id="POSTCONDITION_FAILURE",
                description="Function postcondition not established by implementation",
                proof_obligation_type="postcondition",
                keywords=["postcondition", "ensures", "post", "return", "assert", "assertion", "assigns", "modifies", "frame"],
                examples=[]
            ),
            SemanticPrimitive(
                primitive_id="LOOP_INVARIANT_VIOLATION",
                description="Loop invariant not established or preserved",
                proof_obligation_type="invariant",
                keywords=["invariant", "loop", "preservation", "maintenance", "establishment", "induction"],
                examples=[]
            ),
            SemanticPrimitive(
                primitive_id="BOUNDS_CHECK_FAILURE",
                description="Array or sequence index out of bounds",
                proof_obligation_type="bounds_check",
                keywords=["bounds", "index", "array", "range", "sequence"],
                examples=[]
            ),
            SemanticPrimitive(
                primitive_id="ARITHMETIC_OVERFLOW",
                description="Integer arithmetic overflow or underflow",
                proof_obligation_type="arithmetic_safety",
                keywords=["overflow", "underflow", "integer", "arithmetic", "division", "zero", "div"],
                examples=[]
            ),
            SemanticPrimitive(
                primitive_id="NULL_DEREFERENCE",
                description="Dereferencing potentially null pointer or reference",
                proof_obligation_type="memory_safety",
                keywords=["null", "dereference", "pointer", "memory", "initialized"],
                examples=[]
            ),
            SemanticPrimitive(
                primitive_id="TERMINATION_FAILURE",
                description="Termination metric does not decrease",
                proof_obligation_type="termination",
                keywords=["variant", "decreases", "termination", "decrease"],
                examples=[]
            ),
            SemanticPrimitive(
                primitive_id="TYPE_MISMATCH",
                description="Type constraint or invariant violation",
                proof_obligation_type="type_safety",
                keywords=["type", "constraint", "invariant", "newtype"],
                examples=[]
            ),
        ]

    def cluster_by_proof_obligation(
        self,
        categories: Dict[str, List[ErrorCategory]]
    ) -> List[SemanticPrimitive]:
        """Group categories by proof obligation semantics."""
        # For this PoC, we use the predefined primitives
        # In a full implementation, this would analyze category descriptions
        # and dynamically cluster them
        return self.primitive_definitions

    def export_taxonomy(self, primitives: List[SemanticPrimitive], output_path: str) -> None:
        """Save taxonomy to YAML file."""
        import yaml

        data = {
            "primitives": [p.to_dict() for p in primitives]
        }

        with open(output_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
