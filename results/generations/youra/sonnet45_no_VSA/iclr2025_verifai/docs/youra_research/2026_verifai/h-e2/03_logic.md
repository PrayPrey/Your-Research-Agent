# Logic Design: H-E2

**Date:** 2026-07-11  
**Hypothesis:** Common semantic primitives exist across verifiers (Frama-C, Dafny, Why3) that can be abstracted into universal repair categories  
**Type:** EXISTENCE (PoC)  
**Phase:** 3 - Implementation Planning  

---

## Codebase Analysis (Serena)

**Project Type**: Green-field  
**Status**: New taxonomy analysis implementation - no existing base hypothesis  
**Analyzed Path**: N/A (no prior codebase for H-E2)  
**Relevant Symbols**: None - designing new taxonomy construction pipeline  

**Note**: This is a foundation hypothesis (Wave 1) with no prerequisites. H-E1 exists in parallel but focuses on iterative repair, not taxonomy construction.

---

## Core Components

### L-1: Error Category Extraction [Complexity: 2, Budget: 8]

**Applied**: Standard Python data extraction patterns

#### API Signatures

```python
from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum

class VerifierType(Enum):
    FRAMA_C = "frama-c"
    DAFNY = "dafny"
    WHY3 = "why3"

@dataclass
class ErrorCategory:
    """Single error category from a verifier."""
    verifier: VerifierType
    category_name: str
    description: str
    source: str  # "documentation" | "empirical"
    examples: List[str]

class DocumentationParser:
    """Extract error categories from verifier documentation."""
    
    def parse_frama_c_docs(self, doc_path: str) -> List[ErrorCategory]:
        """Parse Frama-C WP documentation. Returns VC types."""
        ...
    
    def parse_dafny_docs(self, doc_path: str) -> List[ErrorCategory]:
        """Parse Dafny error documentation. Returns verification failure types."""
        ...
    
    def parse_why3_docs(self, doc_path: str) -> List[ErrorCategory]:
        """Parse Why3 Model_parser API. Returns error model element types."""
        ...

class EmpiricalRunner:
    """Collect error categories by running verifiers on benchmark programs."""
    
    def run_verifier(
        self, 
        verifier: VerifierType, 
        program_path: str
    ) -> List[ErrorCategory]:
        """Execute verifier on program, parse output for error categories."""
        ...
    
    def collect_from_benchmarks(
        self, 
        verifier: VerifierType, 
        benchmark_dir: str
    ) -> List[ErrorCategory]:
        """Run verifier on all programs in benchmark directory."""
        ...

class CategoryExtractor:
    """Main extraction orchestrator."""
    
    def __init__(self):
        self.doc_parser = DocumentationParser()
        self.empirical_runner = EmpiricalRunner()
    
    def extract_all_categories(self) -> Dict[VerifierType, List[ErrorCategory]]:
        """Extract from docs + empirical runs. Returns: {verifier: [categories]}"""
        ...
    
    def export_catalog(self, categories: Dict, output_path: str) -> None:
        """Save to error_categories.json."""
        ...
```

#### Data Structures

```python
# error_categories.json structure
{
    "frama-c": [
        {
            "category_name": "precondition_holds",
            "description": "Verify function precondition holds at call site",
            "source": "documentation",
            "examples": ["WP goal: requires clause"]
        }
    ],
    "dafny": [...],
    "why3": [...]
}
```

#### Pseudo-code

```
1. For each verifier in [frama-c, dafny, why3]:
   a. Parse official documentation → extract category list
   b. Run verifier on benchmark programs → collect empirical instances
   c. Deduplicate categories (doc + empirical)
   d. Store: {verifier: [ErrorCategory]}
2. Export to error_categories.json
```

#### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Doc parser (Frama-C) | Parse WP manual for VC types |
| L-1-2 | Doc parser (Dafny) | Parse error docs for verification failures |
| L-1-3 | Doc parser (Why3) | Parse Model_parser API for error elements |
| L-1-4 | Empirical runner | Execute verifiers on benchmarks |
| L-1-5 | Error parser | Parse verifier output to ErrorCategory |
| L-1-6 | Category deduplication | Merge doc + empirical categories |
| L-1-7 | JSON export | Save catalog to error_categories.json |
| L-1-8 | Unit tests | Validate parsers on sample data |

---

### L-2: Semantic Primitive Identification [Complexity: 3, Budget: 12]

**Applied**: Clustering pattern for semantic grouping

#### API Signatures

```python
from typing import List, Dict, Tuple, Set

@dataclass
class SemanticPrimitive:
    """Universal repair category."""
    primitive_id: str  # "MISSING_PRECONDITION"
    description: str
    proof_obligation_type: str  # "precondition" | "postcondition" | "invariant" | ...
    examples: List[str]  # Example error categories mapping to this

class SemanticClusterer:
    """Identify semantic primitives through bottom-up clustering."""
    
    def __init__(self, primitives_seed: List[str]):
        """Initialize with candidate primitive list from Phase 2C."""
        self.primitives = [
            "MISSING_PRECONDITION",
            "POSTCONDITION_FAILURE",
            "LOOP_INVARIANT_VIOLATION",
            "BOUNDS_CHECK_FAILURE",
            "ARITHMETIC_OVERFLOW",
            "NULL_DEREFERENCE",
            "TERMINATION_FAILURE",
            "TYPE_MISMATCH"
        ]
    
    def cluster_by_proof_obligation(
        self, 
        categories: Dict[VerifierType, List[ErrorCategory]]
    ) -> List[SemanticPrimitive]:
        """Group categories by proof obligation semantics. Returns primitives."""
        ...
    
    def validate_coverage(
        self, 
        primitives: List[SemanticPrimitive], 
        categories: Dict
    ) -> Tuple[float, Dict[str, int]]:
        """Check if primitives cover categories. Returns (coverage_pct, unmapped_counts)."""
        ...

class TaxonomySpecifier:
    """Generate taxonomy specification document."""
    
    def define_primitive(
        self, 
        primitive_id: str, 
        examples: List[ErrorCategory]
    ) -> SemanticPrimitive:
        """Create primitive definition from clustered examples."""
        ...
    
    def export_taxonomy(
        self, 
        primitives: List[SemanticPrimitive], 
        output_path: str
    ) -> None:
        """Save to semantic_primitives.yaml."""
        ...
```

#### Data Structures

```python
# semantic_primitives.yaml structure
primitives:
  - primitive_id: "MISSING_PRECONDITION"
    description: "Function precondition not satisfied at call site"
    proof_obligation_type: "precondition"
    examples:
      - "frama-c: precondition_holds"
      - "dafny: precondition_violation"
  - primitive_id: "LOOP_INVARIANT_VIOLATION"
    ...
```

#### Pseudo-code

```
1. Load error categories from L-1
2. For each candidate primitive:
   a. Identify matching categories by semantic keywords (precondition, overflow, etc.)
   b. Group categories under primitive
3. Validate coverage:
   a. Count mapped vs total categories
   b. If coverage < 80%, expand primitive set
4. Export taxonomy to semantic_primitives.yaml
```

#### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Primitive seed initialization | Load candidate primitives from Phase 2C |
| L-2-2 | Keyword extraction | Extract semantic keywords from category descriptions |
| L-2-3 | Clustering logic | Group categories by proof obligation type |
| L-2-4 | Primitive definition | Generate definition from clustered examples |
| L-2-5 | Coverage validator | Compute (mapped / total) × 100% |
| L-2-6 | Unmapped analyzer | Identify categories not matching primitives |
| L-2-7 | Primitive expansion | Add new primitives if coverage low |
| L-2-8 | Taxonomy YAML export | Save to semantic_primitives.yaml |
| L-2-9 | Visualization (heatmap) | Show category-to-primitive mapping |
| L-2-10 | Unit tests | Test clustering on sample data |
| L-2-11 | Edge case documentation | Document categories resisting abstraction |
| L-2-12 | Expert review prep | Generate taxonomy report for validation |

---

### L-3: Mapping Construction [Complexity: 3, Budget: 14]

**Applied**: Rule-based mapping with confidence scoring

#### API Signatures

```python
from typing import Optional, Tuple, Dict

@dataclass
class Mapping:
    """Single verifier error → semantic primitive mapping."""
    verifier: VerifierType
    error_category: str
    semantic_primitive: Optional[str]  # None if unmapped
    confidence_score: float  # 0.0-1.0
    notes: str  # Edge case documentation

class MappingEngine:
    """Map verifier errors to semantic primitives."""
    
    def __init__(
        self, 
        primitives: List[SemanticPrimitive], 
        categories: Dict[VerifierType, List[ErrorCategory]]
    ):
        self.primitives = primitives
        self.categories = categories
        self.mappings: List[Mapping] = []
    
    def compute_semantic_similarity(
        self, 
        category: ErrorCategory, 
        primitive: SemanticPrimitive
    ) -> float:
        """Heuristic: keyword overlap + proof obligation type match. Returns 0.0-1.0."""
        ...
    
    def map_category(self, category: ErrorCategory) -> Mapping:
        """Find best primitive match for category. Returns mapping with confidence."""
        ...
    
    def map_all_categories(self) -> List[Mapping]:
        """Generate mappings for all categories across all verifiers."""
        ...
    
    def export_mappings(self, output_path: str) -> None:
        """Save to taxonomy_mapping.json."""
        ...

class ConfidenceScorer:
    """Compute confidence scores for mappings."""
    
    def score_keyword_overlap(self, category: ErrorCategory, primitive: SemanticPrimitive) -> float:
        """Jaccard similarity on description keywords. Returns 0.0-1.0."""
        ...
    
    def score_proof_obligation_match(self, category: ErrorCategory, primitive: SemanticPrimitive) -> float:
        """Binary: 1.0 if proof obligation types match, 0.5 otherwise."""
        ...
    
    def aggregate_score(self, keyword_score: float, po_score: float) -> float:
        """Weighted average: 0.6 × keyword + 0.4 × proof_obligation."""
        ...
```

#### Data Structures

```python
# taxonomy_mapping.json structure
{
    "mappings": [
        {
            "verifier": "frama-c",
            "error_category": "precondition_holds",
            "semantic_primitive": "MISSING_PRECONDITION",
            "confidence_score": 1.0,
            "notes": "Direct semantic match"
        },
        {
            "verifier": "why3",
            "error_category": "loop_current_iteration",
            "semantic_primitive": "LOOP_INVARIANT_VIOLATION",
            "confidence_score": 0.8,
            "notes": "Inferred from loop context"
        }
    ]
}
```

#### Pseudo-code

```
1. Load primitives from L-2, categories from L-1
2. For each category in each verifier:
   a. For each primitive:
      i. Compute keyword overlap score
      ii. Compute proof obligation match score
      iii. Aggregate scores
   b. Select primitive with highest score (if score ≥ 0.5)
   c. Create Mapping(category, primitive, score, notes)
3. Export to taxonomy_mapping.json
```

#### Subtasks [14/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Keyword extractor | Extract keywords from category/primitive descriptions |
| L-3-2 | Jaccard similarity | Compute keyword overlap |
| L-3-3 | Proof obligation matcher | Match category/primitive PO types |
| L-3-4 | Confidence aggregator | Weighted average of scores |
| L-3-5 | Best match selector | Choose primitive with max confidence |
| L-3-6 | Threshold filter | Map only if confidence ≥ 0.5 |
| L-3-7 | Unmapped handler | Document categories with no match |
| L-3-8 | Edge case annotator | Add notes for low-confidence mappings |
| L-3-9 | Multi-primitive support | Allow category → multiple primitives |
| L-3-10 | JSON export | Save to taxonomy_mapping.json |
| L-3-11 | Visualization (heatmap) | Show verifier × primitive mapping grid |
| L-3-12 | Unit tests | Test mapping on sample data |
| L-3-13 | Manual override support | Allow expert to adjust mappings |
| L-3-14 | Mapping validation | Check all categories processed |

---

### L-4: Coverage Computation & Gate Validation [Complexity: 2, Budget: 8]

**Applied**: Standard metric computation patterns

#### API Signatures

```python
from typing import Dict, List

@dataclass
class CoverageMetrics:
    """Coverage statistics for taxonomy validation."""
    aggregate_coverage: float  # (mapped / total) × 100%
    per_verifier_coverage: Dict[VerifierType, float]
    unmapped_categories: Dict[VerifierType, List[str]]
    primitive_frequencies: Dict[str, int]
    gate_passed: bool  # aggregate ≥ 80% AND all verifiers ≥ 80%

class CoverageComputer:
    """Compute taxonomy coverage metrics."""
    
    def __init__(self, mappings: List[Mapping]):
        self.mappings = mappings
    
    def compute_aggregate_coverage(self) -> float:
        """Total mapped categories / total categories × 100%."""
        ...
    
    def compute_per_verifier_coverage(self) -> Dict[VerifierType, float]:
        """Coverage for each verifier individually."""
        ...
    
    def identify_unmapped_categories(self) -> Dict[VerifierType, List[str]]:
        """List categories with no primitive mapping (confidence < 0.5)."""
        ...
    
    def compute_primitive_frequencies(self) -> Dict[str, int]:
        """Count how many categories map to each primitive."""
        ...
    
    def validate_gate_threshold(self, metrics: CoverageMetrics) -> bool:
        """Check if aggregate ≥ 80% AND all verifiers ≥ 80%."""
        ...
    
    def export_report(self, metrics: CoverageMetrics, output_path: str) -> None:
        """Save to coverage_report.json."""
        ...

class CoverageVisualizer:
    """Generate coverage visualizations."""
    
    def plot_verifier_coverage_bars(
        self, 
        per_verifier: Dict[VerifierType, float], 
        threshold: float = 80.0
    ) -> None:
        """Bar chart with 80% threshold line. Saves to figures/coverage_bars.png."""
        ...
    
    def plot_primitive_frequencies(self, frequencies: Dict[str, int]) -> None:
        """Bar chart of error counts per primitive. Saves to figures/primitive_freq.png."""
        ...
    
    def plot_mapping_heatmap(self, mappings: List[Mapping]) -> None:
        """Heatmap: verifier × primitive. Saves to figures/mapping_heatmap.png."""
        ...
```

#### Coverage Formula

```python
# Aggregate coverage
total_categories = sum(len(categories[v]) for v in categories)
mapped_categories = sum(1 for m in mappings if m.semantic_primitive is not None)
aggregate_coverage = (mapped_categories / total_categories) * 100

# Per-verifier coverage
for verifier in [FRAMA_C, DAFNY, WHY3]:
    verifier_total = len(categories[verifier])
    verifier_mapped = sum(1 for m in mappings if m.verifier == verifier and m.semantic_primitive is not None)
    per_verifier_coverage[verifier] = (verifier_mapped / verifier_total) * 100

# Gate validation
gate_passed = (
    aggregate_coverage >= 80.0 
    and all(coverage >= 80.0 for coverage in per_verifier_coverage.values())
)
```

#### Data Structures

```python
# coverage_report.json structure
{
    "aggregate_coverage": 85.2,
    "per_verifier_coverage": {
        "frama-c": 87.5,
        "dafny": 84.0,
        "why3": 83.8
    },
    "unmapped_categories": {
        "frama-c": ["rare_vc_type_1"],
        "dafny": [],
        "why3": ["other_error"]
    },
    "primitive_frequencies": {
        "MISSING_PRECONDITION": 42,
        "LOOP_INVARIANT_VIOLATION": 38,
        ...
    },
    "gate_passed": true,
    "threshold": 80.0
}
```

#### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Aggregate coverage | Compute (mapped / total) × 100% |
| L-4-2 | Per-verifier coverage | Breakdown by Frama-C, Dafny, Why3 |
| L-4-3 | Unmapped identifier | List categories with no mapping |
| L-4-4 | Primitive frequency counter | Count mappings per primitive |
| L-4-5 | Gate validator | Check ≥80% threshold |
| L-4-6 | JSON export | Save to coverage_report.json |
| L-4-7 | Visualization (bars) | Coverage bars with threshold |
| L-4-8 | Visualization (heatmap) | Verifier × primitive heatmap |

---

## Main Pipeline Orchestrator

**Applied**: Standard pipeline orchestration pattern

### API Signature

```python
class TaxonomyBuilder:
    """Main pipeline: error extraction → primitives → mapping → coverage."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.extractor = CategoryExtractor()
        self.clusterer = SemanticClusterer(primitives_seed=config["primitives"])
        self.mapper = None  # Initialized after clustering
        self.coverage_computer = None  # Initialized after mapping
    
    def run_pipeline(self) -> CoverageMetrics:
        """Execute full taxonomy construction pipeline."""
        # L-1: Extract error categories
        categories = self.extractor.extract_all_categories()
        self.extractor.export_catalog(categories, "data/error_categories.json")
        
        # L-2: Identify semantic primitives
        primitives = self.clusterer.cluster_by_proof_obligation(categories)
        TaxonomySpecifier().export_taxonomy(primitives, "data/semantic_primitives.yaml")
        
        # L-3: Construct mappings
        self.mapper = MappingEngine(primitives, categories)
        mappings = self.mapper.map_all_categories()
        self.mapper.export_mappings("data/taxonomy_mapping.json")
        
        # L-4: Compute coverage & validate gate
        self.coverage_computer = CoverageComputer(mappings)
        metrics = CoverageMetrics(
            aggregate_coverage=self.coverage_computer.compute_aggregate_coverage(),
            per_verifier_coverage=self.coverage_computer.compute_per_verifier_coverage(),
            unmapped_categories=self.coverage_computer.identify_unmapped_categories(),
            primitive_frequencies=self.coverage_computer.compute_primitive_frequencies(),
            gate_passed=self.coverage_computer.validate_gate_threshold(metrics)
        )
        self.coverage_computer.export_report(metrics, "results/coverage_report.json")
        
        # Generate visualizations
        visualizer = CoverageVisualizer()
        visualizer.plot_verifier_coverage_bars(metrics.per_verifier_coverage)
        visualizer.plot_primitive_frequencies(metrics.primitive_frequencies)
        visualizer.plot_mapping_heatmap(mappings)
        
        return metrics
```

---

## Edge Cases & Failure Handling

### Unmapped Categories

**Scenario**: Error category has no semantic primitive match (confidence < 0.5)

**Handling**:
1. Document in `notes` field of Mapping
2. Add to `unmapped_categories` list in coverage report
3. If unmapped count is high (>20% of categories):
   - Review unmapped list for common patterns
   - Propose new semantic primitive
   - Re-run clustering with expanded primitive set

### Verifier-Specific Edge Cases

**Scenario**: Category semantics are tool-specific (e.g., Why3 "Old" values)

**Handling**:
1. Allow low-confidence mapping (0.3-0.5 range)
2. Document tool-specific semantics in `notes`
3. Flag for expert review
4. Consider multi-primitive mapping (category → [primitive1, primitive2])

### Coverage Below Threshold

**Scenario**: Aggregate coverage < 80% after initial mapping

**Mitigation Strategy**:
1. Analyze unmapped categories for semantic clusters
2. Expand primitive set (add 1-3 new primitives)
3. Re-run mapping with expanded taxonomy
4. If still below 60% → MUST_WORK gate fails (hypothesis invalid)

### Documentation Parsing Failures

**Scenario**: Web scraping fails or docs have changed

**Fallback**:
1. Use local cached snapshots of documentation
2. Supplement with empirical error collection (run more benchmarks)
3. Manual curation from documentation PDFs

---

## Data Flow Summary

```
Input: Verifier docs + benchmark programs
  ↓
[L-1: CategoryExtractor]
  → error_categories.json: {verifier: [ErrorCategory]}
  ↓
[L-2: SemanticClusterer]
  → semantic_primitives.yaml: [SemanticPrimitive]
  ↓
[L-3: MappingEngine]
  → taxonomy_mapping.json: [Mapping(category, primitive, confidence)]
  ↓
[L-4: CoverageComputer]
  → coverage_report.json: {aggregate, per_verifier, gate_passed}
  → figures/: coverage_bars.png, primitive_freq.png, mapping_heatmap.png
```

---

## Validation Checklist

**Self-Validation**:
- [x] No ASCII diagrams (text descriptions only)
- [x] KB search result: "Applied: Standard patterns" (1 line)
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes not applicable (data structures documented)
- [x] Subtask counts within budgets (L-1: 8/8, L-2: 12/12, L-3: 14/14, L-4: 8/8)
- [x] Total length ~500 lines
- [x] Codebase Analysis section included
- [x] Green-field project noted (Serena skip acceptable)

**Phase 4 Readiness**:
- [x] All class/function signatures with type hints
- [x] Data structure schemas defined (JSON/YAML)
- [x] Pseudo-code for complex algorithms (clustering, mapping)
- [x] Coverage formula explicitly stated
- [x] Edge case handling documented

---

**Status:** READY FOR PHASE 4  
**Next Step:** Phase 4 - Implementation (taxonomy_builder.py + extractors + evaluation)  
**Owner:** Phase 4 Coder Agent
