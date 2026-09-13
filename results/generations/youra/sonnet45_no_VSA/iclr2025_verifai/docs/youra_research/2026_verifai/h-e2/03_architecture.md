# System Architecture: H-E2 Cross-Verifier Semantic Taxonomy

**Date:** 2026-07-11  
**Hypothesis:** H-E2 - Common semantic primitives exist across verifiers (Frama-C, Dafny, Why3) that can be abstracted into universal repair categories  
**PRD:** 03_prd.md  
**Experiment Brief:** 02c_experiment_brief.md  
**Architecture Type:** EXISTENCE (PoC) - Taxonomy construction pipeline  

---

## Knowledge Base Application

Applied: Data extraction pipeline patterns, taxonomy construction architecture  

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** Patterns found from H-E1 code structure  
**Analyzed Path:** docs/youra_research/h-e1/code/  
**Findings:** Established module pattern with src/ structure, config-driven execution, metrics tracking, visualization generation. H-E2 follows similar orchestration pattern for taxonomy pipeline.

---

## System Context

### Core Hypothesis Test

**Question:** Do Frama-C, Dafny, and Why3 share sufficient semantic primitives to enable a universal error taxonomy with ≥80% coverage?

**Mechanism:** Cross-verifier taxonomy construction through documentation extraction, semantic clustering, and mapping validation.

**Success Criteria:**
- Aggregate coverage ≥80% across all verifiers (MUST_WORK gate)
- Per-verifier coverage ≥80% (Frama-C, Dafny, Why3 individually)
- Abstraction layer design is implementation-ready

### System Boundaries

**Input:**
- Verifier documentation (Frama-C WP API, Dafny error docs, Why3 Model_parser API)
- Benchmark programs (Frama-C examples, Juliet verified subset, Why3 gallery)

**Output:**
- error_categories.json (verifier-specific error catalog)
- semantic_primitives.yaml (universal repair category taxonomy)
- taxonomy_mapping.json (verifier-to-primitive mappings with confidence scores)
- coverage_report.json (metrics + gate validation)
- figures/ (heatmap, coverage bars, unmapped analysis)

**External Dependencies:**
- Frama-C 28.1 (WP plugin)
- Dafny 4.9.0
- Why3 1.7.2 + Alt-Ergo/Z3 SMT solvers
- Python 3.10+ (pandas, pyyaml, matplotlib, seaborn, BeautifulSoup)

**Out of Scope (PoC):**
- Multi-primitive assignments (one error → multiple primitives) - simplified to single mapping
- Automated clustering algorithms - manual semantic grouping
- Expert validation - automated threshold validation only
- Cross-verifier repair strategy validation - taxonomy construction only

---

## Module Structure

### 1. DocumentationExtractor (`src/extractors/doc_extractor.py`)

**Dependencies:** requests, BeautifulSoup, yaml

```python
class DocumentationExtractor:
    def __init__(self, cache_dir: str = "data/cache"): ...
    def extract_frama_c_categories(self) -> list[ErrorCategory]: ...
    def extract_dafny_categories(self) -> list[ErrorCategory]: ...
    def extract_why3_categories(self) -> list[ErrorCategory]: ...
    def _scrape_url(self, url: str) -> str: ...
    def _parse_frama_c_docs(self, html: str) -> list[ErrorCategory]: ...
    def _parse_dafny_docs(self, html: str) -> list[ErrorCategory]: ...
    def _parse_why3_docs(self, html: str) -> list[ErrorCategory]: ...

class ErrorCategory:
    verifier: str
    category_name: str
    description: str
    example: str
    source_url: str
```

### 2. EmpiricalExtractor (`src/extractors/empirical_extractor.py`)

**Dependencies:** subprocess, tempfile, pathlib

```python
class EmpiricalExtractor:
    def __init__(self, verifier_configs: dict): ...
    def run_frama_c(self, c_files: list[str]) -> list[ErrorInstance]: ...
    def run_dafny(self, dfy_files: list[str]) -> list[ErrorInstance]: ...
    def run_why3(self, why_files: list[str]) -> list[ErrorInstance]: ...
    def _execute_verifier(self, cmd: list[str], file_path: str) -> str: ...
    def _parse_error_output(self, verifier: str, output: str) -> list[ErrorInstance]: ...

class ErrorInstance:
    verifier: str
    category: str
    error_message: str
    file_path: str
    line_number: int
```

### 3. SemanticClusterer (`src/clustering/semantic_clusterer.py`)

**Dependencies:** None (manual semantic grouping)

```python
class SemanticClusterer:
    def __init__(self, primitives_config: str = "config/primitives.yaml"): ...
    def identify_primitives(self, error_categories: list[ErrorCategory]) -> list[SemanticPrimitive]: ...
    def _load_predefined_primitives(self) -> list[SemanticPrimitive]: ...
    def _validate_coverage(self, primitives: list[SemanticPrimitive], categories: list[ErrorCategory]) -> float: ...

class SemanticPrimitive:
    primitive_id: str
    name: str
    description: str
    proof_obligation_type: str
    examples: list[str]
```

### 4. MappingEngine (`src/mapping/mapping_engine.py`)

**Dependencies:** SemanticClusterer, DocumentationExtractor

```python
class MappingEngine:
    def __init__(self, primitives: list[SemanticPrimitive]): ...
    def map_category_to_primitive(self, category: ErrorCategory) -> Mapping: ...
    def compute_confidence(self, category: ErrorCategory, primitive: SemanticPrimitive) -> float: ...
    def build_mapping_table(self, categories: list[ErrorCategory]) -> list[Mapping]: ...
    def _apply_mapping_rules(self, verifier: str, category_name: str) -> tuple[str, float]: ...

class Mapping:
    verifier: str
    error_category: str
    semantic_primitive: str | None
    confidence_score: float
    notes: str
```

### 5. CoverageComputer (`src/evaluation/coverage_computer.py`)

**Dependencies:** MappingEngine

```python
class CoverageComputer:
    def __init__(self, threshold: float = 0.5): ...
    def compute_aggregate_coverage(self, mappings: list[Mapping]) -> float: ...
    def compute_per_verifier_coverage(self, mappings: list[Mapping]) -> dict[str, float]: ...
    def identify_unmapped_categories(self, mappings: list[Mapping]) -> list[UnmappedCategory]: ...
    def validate_gate_threshold(self, coverage: float, gate_threshold: float = 80.0) -> bool: ...

class UnmappedCategory:
    verifier: str
    category: str
    reason: str
```

### 6. Visualizer (`src/evaluation/visualizer.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
class Visualizer:
    def __init__(self, output_dir: str = "figures"): ...
    def plot_taxonomy_heatmap(self, mappings: list[Mapping], output_path: str): ...
    def plot_coverage_breakdown(self, per_verifier_coverage: dict[str, float], threshold: float, output_path: str): ...
    def plot_primitive_frequency(self, mappings: list[Mapping], output_path: str): ...
    def plot_gate_comparison(self, actual_coverage: float, target_coverage: float, output_path: str): ...
    def _create_mapping_matrix(self, mappings: list[Mapping]) -> pd.DataFrame: ...
```

### 7. TaxonomyBuilder (`src/taxonomy_builder.py`)

**Dependencies:** All above modules

```python
class TaxonomyBuilder:
    def __init__(self, config_path: str): ...
    def run_pipeline(self) -> dict: ...
    def _phase1_extract_categories(self) -> list[ErrorCategory]: ...
    def _phase2_identify_primitives(self, categories: list[ErrorCategory]) -> list[SemanticPrimitive]: ...
    def _phase3_construct_mappings(self, categories: list[ErrorCategory], primitives: list[SemanticPrimitive]) -> list[Mapping]: ...
    def _phase4_compute_coverage(self, mappings: list[Mapping]) -> dict: ...
    def _save_outputs(self, categories, primitives, mappings, coverage): ...
```

### 8. Main Orchestrator (`src/main.py`)

**Dependencies:** TaxonomyBuilder, yaml, pathlib

```python
class ExperimentRunner:
    def __init__(self, config_path: str): ...
    def run_experiment(self) -> dict: ...
    def _load_config(self) -> dict: ...
    def _validate_prerequisites(self) -> bool: ...
    def _execute_pipeline(self) -> dict: ...
    def _generate_report(self, results: dict) -> dict: ...
```

---

## Data Flow

### Pipeline Stages

1. **Phase 1: Error Category Extraction**
   - Input: Verifier documentation URLs, benchmark program paths
   - Process: DocumentationExtractor + EmpiricalExtractor
   - Output: error_categories.json (structured catalog)

2. **Phase 2: Semantic Primitive Identification**
   - Input: error_categories.json
   - Process: SemanticClusterer (manual semantic grouping)
   - Output: semantic_primitives.yaml (taxonomy specification)

3. **Phase 3: Mapping Construction**
   - Input: error_categories.json, semantic_primitives.yaml
   - Process: MappingEngine (rule-based mapping + confidence scoring)
   - Output: taxonomy_mapping.json (verifier × category → primitive + confidence)

4. **Phase 4: Coverage Computation & Validation**
   - Input: taxonomy_mapping.json
   - Process: CoverageComputer + Visualizer
   - Output: coverage_report.json, figures/ (heatmap, coverage bars, gate comparison)

### Data Structures

**error_categories.json:**
```json
[
  {
    "verifier": "frama-c",
    "category_name": "memory_access_valid",
    "description": "Valid memory access check",
    "example": "...",
    "source_url": "https://frama-c.com/api/..."
  }
]
```

**semantic_primitives.yaml:**
```yaml
primitives:
  - primitive_id: MISSING_PRECONDITION
    name: Missing Precondition
    description: Precondition not satisfied at function call
    proof_obligation_type: contract_violation
    examples: [Frama-C precondition_holds, Dafny precondition_violation]
```

**taxonomy_mapping.json:**
```json
[
  {
    "verifier": "frama-c",
    "error_category": "precondition_holds",
    "semantic_primitive": "MISSING_PRECONDITION",
    "confidence_score": 1.0,
    "notes": "Direct semantic match"
  }
]
```

**coverage_report.json:**
```json
{
  "aggregate_coverage": 85.7,
  "per_verifier_coverage": {
    "frama-c": 88.2,
    "dafny": 84.6,
    "why3": 84.2
  },
  "gate_threshold": 80.0,
  "gate_passed": true,
  "unmapped_categories_count": 12,
  "total_categories_count": 84
}
```

---

## File Organization

```
h-e2/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                     # Main experiment orchestrator
│   │   ├── taxonomy_builder.py          # Pipeline coordinator
│   │   ├── extractors/
│   │   │   ├── __init__.py
│   │   │   ├── doc_extractor.py         # Documentation scraping
│   │   │   └── empirical_extractor.py   # Verifier execution
│   │   ├── clustering/
│   │   │   ├── __init__.py
│   │   │   └── semantic_clusterer.py    # Primitive identification
│   │   ├── mapping/
│   │   │   ├── __init__.py
│   │   │   └── mapping_engine.py        # Category → primitive mapping
│   │   └── evaluation/
│   │       ├── __init__.py
│   │       ├── coverage_computer.py     # Metrics computation
│   │       └── visualizer.py            # Figure generation
│   ├── config/
│   │   ├── experiment.yaml              # Main configuration
│   │   ├── primitives.yaml              # Semantic primitive definitions
│   │   └── verifiers.yaml               # Verifier-specific settings
│   ├── data/
│   │   ├── cache/                       # Cached documentation
│   │   ├── benchmarks/                  # Downloaded benchmark programs
│   │   ├── error_categories.json        # Extracted error catalog
│   │   ├── semantic_primitives.yaml     # Taxonomy specification
│   │   └── taxonomy_mapping.json        # Mapping table
│   ├── results/
│   │   └── coverage_report.json         # Metrics + gate validation
│   ├── figures/
│   │   ├── taxonomy_heatmap.png
│   │   ├── coverage_breakdown.png
│   │   ├── primitive_frequency.png
│   │   └── gate_comparison.png
│   ├── requirements.txt
│   └── README.md
└── 03_architecture.md (this document)
```

---

## Technology Stack

### Core Technologies
- Python 3.10+
- Verifier toolchains:
  - Frama-C 28.1 (WP plugin)
  - Dafny 4.9.0
  - Why3 1.7.2 + Alt-Ergo 2.6.2 + Z3 4.15.2

### Python Libraries
- Data processing: pandas, pyyaml, json
- Web scraping: requests, BeautifulSoup4
- Visualization: matplotlib, seaborn
- Subprocess management: subprocess, tempfile
- Utilities: pathlib, typing, dataclasses

### Rationale
- **Python:** Standard for data processing pipelines, rich ecosystem for taxonomy analysis
- **pandas:** Efficient DataFrame operations for mapping table manipulation
- **BeautifulSoup:** Robust HTML parsing for documentation extraction
- **matplotlib/seaborn:** Publication-quality visualization (heatmap, bar charts)
- **Pinned verifier versions:** Reproducibility guarantee (NFR-1)

---

## Integration Points

### Verifier-Specific Adapters

**Frama-C WP Adapter:**
- API endpoint: https://frama-c.com/api/frama-c-wp/Wp/VC/index.html
- Execution command: `frama-c -wp -wp-timeout 10 -wp-prover alt-ergo,z3 <file.c>`
- Error extraction: Parse VC types from WP output (memory_safety, arithmetic_safety, functional_property, termination)

**Dafny Adapter:**
- Documentation: https://dafny.org/v3.12.0/HowToFAQ/Errors
- Execution command: `dafny verify <file.dfy>`
- Error extraction: Parse verification errors from JSON output (precondition_violation, postcondition_violation, invariant_violation, decreases_violation)

**Why3 Adapter:**
- API endpoint: https://why3.org/api/Model_parser.html
- Execution command: `why3 prove -P alt-ergo,z3 <file.why>`
- Error extraction: Parse model elements from SMT solver output (Error_message, Result, Loop_before, Loop_current, Loc.position, Old, Other)

### Benchmark Program Sources

**Frama-C Examples:**
- Repository: https://git.frama-c.com/pub/frama-c (examples/ directory)
- Download method: `git clone https://git.frama-c.com/pub/frama-c.git`
- Filter: C programs with ACSL annotations

**Juliet Test Suite (Verified Subset):**
- Repository: NIST Juliet Test Suite for static analyzers
- Download method: Manual download from NIST SAMATE
- Filter: Programs with formal verification compatibility

**Why3 Gallery:**
- Repository: https://why3.org/gallery/
- Download method: `git clone https://gitlab.inria.fr/why3/why3.git` (gallery/ directory)
- Filter: Examples with proof obligations

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup project structure | Initialize file structure, install verifiers, configure environment | 8 | Module:2 + Deps:2 + Algo:2 + Integ:2 |
| A-2 | Implement documentation extractors | Build scrapers for Frama-C, Dafny, Why3 documentation | 14 | Module:3 + Deps:3 + Algo:4 + Integ:4 |
| A-3 | Implement empirical extractors | Build verifier execution harness + error output parsers | 16 | Module:4 + Deps:4 + Algo:4 + Integ:4 |
| A-4 | Implement semantic clusterer | Manual primitive identification + validation logic | 12 | Module:3 + Deps:2 + Algo:4 + Integ:3 |
| A-5 | Implement mapping engine | Build rule-based mapping logic + confidence scoring | 15 | Module:4 + Deps:3 + Algo:4 + Integ:4 |
| A-6 | Implement coverage computer | Build metrics computation + threshold validation | 10 | Module:3 + Deps:2 + Algo:3 + Integ:2 |
| A-7 | Implement visualizer | Build heatmap, coverage bars, frequency plots, gate comparison | 13 | Module:3 + Deps:3 + Algo:3 + Integ:4 |
| A-8 | Implement pipeline orchestrator | Build TaxonomyBuilder + main experiment runner | 11 | Module:3 + Deps:2 + Algo:3 + Integ:3 |
| A-9 | Run experiment + generate report | Execute full pipeline, validate coverage, generate deliverables | 9 | Module:2 + Deps:2 + Algo:2 + Integ:3 |

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): [A-2, A-3, A-5]
- Medium (9-13): [A-4, A-6, A-7, A-8, A-9]
- Low (4-8): [A-1]

**Total Complexity:** 108 (9 tasks)

---

## Validation Strategy

### Coverage Metrics (Automated)

**Aggregate Coverage:**
```python
aggregate_coverage = (mapped_categories / total_categories) × 100
gate_passed = aggregate_coverage >= 80.0
```

**Per-Verifier Coverage:**
```python
per_verifier_coverage = {
    verifier: (mapped_in_verifier / total_in_verifier) × 100
    for verifier in ['frama-c', 'dafny', 'why3']
}
individual_gate_passed = all(cov >= 80.0 for cov in per_verifier_coverage.values())
```

### Unmapped Category Analysis

**Identify categories with confidence < 0.5:**
```python
unmapped = [m for m in mappings if m.confidence_score < 0.5 or m.semantic_primitive is None]
```

**Document tool-specific edge cases:**
- Categories that resist semantic abstraction
- Verifier-specific implementation details
- Proof obligation types unique to one tool

### Gate Validation

**MUST_WORK Gate:**
```python
gate_passed = (
    aggregate_coverage >= 80.0 and
    all(cov >= 80.0 for cov in per_verifier_coverage.values()) and
    abstraction_layer_feasible
)
```

**Failure Condition:**
- Coverage < 60%: Tool-specific semantics dominate, no viable abstraction
- Any verifier < 80%: Abstraction biased toward specific tools
- No clear primitive set emerges: Implementation not feasible

---

## Risk Mitigation

### R1: Coverage Below 80% Threshold
**Likelihood:** Medium  
**Impact:** Critical (MUST_WORK gate fails)  
**Mitigation:**
- Expand semantic primitive set during Phase 2 if initial coverage low
- Document tool-specific edge cases as acceptable unmapped categories (threshold may adjust to exclude edge cases)
- Fallback: Lower gate to 70% if edge cases account for gap

### R2: Verifier Installation Complexity
**Likelihood:** High  
**Impact:** Medium (delays execution)  
**Mitigation:**
- Docker container with pre-installed verifiers (Frama-C 28.1, Dafny 4.9.0, Why3 1.7.2)
- Installation scripts for Ubuntu 22.04 LTS
- Fallback: Skip empirical extraction, rely on documentation only

### R3: Documentation Parsing Failures
**Likelihood:** Low  
**Impact:** Medium (incomplete error catalog)  
**Mitigation:**
- Fallback to manual curation if web scraping fails
- Maintain backup local copies of documentation snapshots
- Supplement with empirical error collection from benchmarks

### R4: Mapping Ambiguity
**Likelihood:** Medium  
**Impact:** Medium (low confidence scores)  
**Mitigation:**
- Document ambiguous mappings with notes field
- Use confidence scoring to flag uncertain mappings
- Manual review of low-confidence mappings (<0.5)

---

## Implementation Timeline

### Week-by-Week Breakdown

**Week 1-2: Setup + Documentation Extraction (A-1, A-2)**
- Install verifiers, configure environment
- Implement DocumentationExtractor for all 3 verifiers
- Cache documentation locally

**Week 3-4: Empirical Extraction + Semantic Clustering (A-3, A-4)**
- Implement EmpiricalExtractor + verifier execution harness
- Run verifiers on benchmark programs (≥100 instances per tool)
- Implement SemanticClusterer + identify primitives

**Week 5-6: Mapping Construction + Coverage Computation (A-5, A-6)**
- Implement MappingEngine with rule-based logic
- Compute confidence scores for all mappings
- Implement CoverageComputer + validate thresholds

**Week 7: Visualization + Pipeline Orchestration (A-7, A-8, A-9)**
- Implement Visualizer (heatmap, coverage bars, frequency, gate comparison)
- Implement TaxonomyBuilder orchestrator
- Run full pipeline, generate deliverables

---

## Success Criteria Summary

**Primary Success (MUST_WORK Gate):**
- Aggregate coverage ≥80%
- Per-verifier coverage ≥80% (Frama-C, Dafny, Why3)
- Abstraction layer design is implementation-ready

**Secondary Success (PoC Validation):**
- Coverage > 0% baseline (semantic overlap exists)
- ≥6 semantic primitives identified
- Mapping table generated for all error categories

**Deliverables:**
- error_categories.json (extracted catalog)
- semantic_primitives.yaml (taxonomy specification)
- taxonomy_mapping.json (mapping table)
- coverage_report.json (metrics + gate validation)
- figures/ (4 visualizations)
- 04_validation.md (experimental results)

---

**Status:** READY FOR PHASE 4 IMPLEMENTATION  
**Next Step:** Phase 4 Coder implements pipeline based on this architecture  
**Gate Validation:** Automated threshold check in coverage_report.json  
**Owner:** Phase 3 Architecture Agent
