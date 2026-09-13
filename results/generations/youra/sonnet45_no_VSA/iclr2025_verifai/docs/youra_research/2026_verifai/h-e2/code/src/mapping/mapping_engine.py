"""Map error categories to semantic primitives with confidence scoring."""

from typing import List, Dict, Optional, Tuple
import json
from ..data_structures import ErrorCategory, SemanticPrimitive, Mapping


class MappingEngine:
    """Map verifier errors to semantic primitives."""

    def __init__(
        self,
        primitives: List[SemanticPrimitive],
        categories: Dict[str, List[ErrorCategory]],
        confidence_threshold: float = 0.5
    ):
        self.primitives = primitives
        self.categories = categories
        self.confidence_threshold = confidence_threshold
        self.mappings: List[Mapping] = []

    def compute_keyword_overlap(
        self,
        category: ErrorCategory,
        primitive: SemanticPrimitive
    ) -> float:
        """Compute Jaccard similarity on description keywords."""
        # Tokenize category description
        cat_tokens = set(category.category_name.lower().split('_'))
        cat_tokens.update(category.description.lower().split())

        # Primitive keywords
        prim_keywords = set(kw.lower() for kw in primitive.keywords)

        # Jaccard similarity
        intersection = cat_tokens & prim_keywords
        union = cat_tokens | prim_keywords

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def compute_semantic_match(
        self,
        category: ErrorCategory,
        primitive: SemanticPrimitive
    ) -> float:
        """Check for direct semantic match in category name."""
        cat_name_lower = category.category_name.lower()
        cat_desc_lower = category.description.lower()

        for keyword in primitive.keywords:
            kw_lower = keyword.lower()
            if kw_lower in cat_name_lower or kw_lower in cat_desc_lower:
                return 1.0

        return 0.0

    def compute_confidence(
        self,
        category: ErrorCategory,
        primitive: SemanticPrimitive
    ) -> float:
        """Compute overall confidence score (0.0-1.0)."""
        keyword_score = self.compute_keyword_overlap(category, primitive)
        semantic_score = self.compute_semantic_match(category, primitive)

        # Weighted average: 60% semantic, 40% keyword overlap
        confidence = 0.6 * semantic_score + 0.4 * keyword_score

        return min(1.0, confidence)

    def map_category(self, category: ErrorCategory) -> Mapping:
        """Find best primitive match for category."""
        best_primitive = None
        best_score = 0.0
        notes = ""

        for primitive in self.primitives:
            score = self.compute_confidence(category, primitive)
            if score > best_score:
                best_score = score
                best_primitive = primitive.primitive_id

        # Check threshold
        if best_score < self.confidence_threshold:
            best_primitive = None
            notes = f"Low confidence ({best_score:.2f}) - no clear mapping"

        return Mapping(
            verifier=category.verifier,
            error_category=category.category_name,
            semantic_primitive=best_primitive,
            confidence_score=best_score,
            notes=notes
        )

    def map_all_categories(self) -> List[Mapping]:
        """Generate mappings for all categories across all verifiers."""
        self.mappings = []

        for verifier, categories in self.categories.items():
            for category in categories:
                mapping = self.map_category(category)
                self.mappings.append(mapping)

        return self.mappings

    def export_mappings(self, output_path: str) -> None:
        """Save mappings to JSON file."""
        data = {
            "mappings": [m.to_dict() for m in self.mappings]
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
