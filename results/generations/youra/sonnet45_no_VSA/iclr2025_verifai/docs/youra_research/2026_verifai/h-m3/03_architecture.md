# System Architecture: H-M3 Cross-Verifier Transfer Learning

**Date:** 2026-07-11  
**Hypothesis:** H-M3 - Semantic normalization enables cross-verifier transfer with ≤20% degradation  
**PRD:** 03_prd.md  
**Experiment Brief:** 02c_experiment_brief.md  
**Architecture Type:** MECHANISM - Transfer learning validation (6 verifier pairs)

---

## Knowledge Base Application

Applied: Layered normalization pattern, Transfer learning architecture with source/target split

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-e2 + h-m1)  
**Status:** Reusing normalization layer from h-e2, refinement pipeline from h-m1  
**Analyzed Path:** h-e2/code/, h-m1/code/  
**Findings:** h-e2 provides MappingEngine and taxonomy structures. h-m1 provides RefinementLoop and FeedbackExtractor. Integration point: inject normalized feedback into h-m1 pipeline.

---

## System Context

### Core Hypothesis Test

**Question:** Does semantic normalization preserve sufficient semantic structure to enable cross-verifier transfer with ≤20% performance degradation?

**Mechanism:** Train feedback→repair mappings on Source Verifier using universal primitives, then transfer learned mappings to Target Verifier.

**Success Criteria:**
1. Cross-verifier degradation ≤20% across all 6 transfer pairs (MUST_WORK gate)
2. Bidirectional symmetry: Degradation(A→B) ≈ Degradation(B→A) within 5pp
3. Normalization coverage ≥80% per verifier

### System Boundaries

**Input:**
- h-e2 taxonomy: semantic_primitives.yaml, taxonomy_mapping.json
- h-m1 pipeline: IterativeRefinementLoop, FeedbackExtractor
- Dataset: 150 verified programs (50 per verifier)

**Output:**
- results/metrics.csv: Proof discharge rates per (source, target, program, iteration)
- results/degradation.csv: Performance degradation per transfer pair
- figures/: Transfer heatmap, degradation bars, convergence curves
- 04_validation.md: Gate decision report

**External Dependencies:**
- Frama-C 28.0 (ACSL verification)
- Dafny 4.0 (Dafny verification)
- Why3 1.6 (WhyML verification)
- Anthropic Claude Opus 4.5 (specification generation)

**Out of Scope:**
- Multi-primitive mappings (one-to-one only)
- Adaptive syntax generation (template-based only)
- Online learning (fixed mappings from training phase)

---

## Module Structure

### 1. CrossVerifierNormalizer (`src/normalizer.py`)

**Dependencies:** h-e2 MappingEngine, h-e2 data_structures

```python
class CrossVerifierNormalizer:
    def __init__(self, taxonomy_path: str, mapping_path: str): ...
    def normalize_feedback(self, verifier: str, raw_output: str) -> NormalizedFeedback: ...
    def get_coverage_stats(self, normalized_batch: list) -> dict: ...

class NormalizedFeedback:
    verifier_source: str
    semantic_primitives: list[str]
    confidence_scores: list[float]
    unmapped_errors: list[str]
    original_context: dict
```

### 2. SyntaxGenerator (`src/syntax_generator.py`)

**Dependencies:** None

```python
class SyntaxGenerator:
    def __init__(self, template_dir: str): ...
    def generate_frama_c_spec(self, repair_action: str, context: dict) -> str: ...
    def generate_dafny_spec(self, repair_action: str, context: dict) -> str: ...
    def generate_why3_spec(self, repair_action: str, context: dict) -> str: ...
    def validate_syntax(self, verifier: str, spec: str) -> bool: ...

class SpecTemplate:
    verifier: str
    primitive_id: str
    template_string: str
    few_shot_examples: list[str]
```

### 3. TransferPipeline (`src/transfer_pipeline.py`)

**Dependencies:** CrossVerifierNormalizer, SyntaxGenerator, h-m1 IterativeRefinementLoop

```python
class TransferPipeline:
    def __init__(
        self,
        normalizer: CrossVerifierNormalizer,
        syntax_generator: SyntaxGenerator,
        base_loop: IterativeRefinementLoop
    ): ...
    def train(
        self, 
        source_verifier: str, 
        programs: list
    ) -> LearnedMappings: ...
    def transfer(
        self, 
        target_verifier: str, 
        learned_mappings: LearnedMappings,
        test_programs: list
    ) -> TransferResults: ...
    def _apply_normalization_layer(
        self, 
        verifier: str, 
        feedback: StructuredFeedback
    ) -> NormalizedFeedback: ...

class LearnedMappings:
    source_verifier: str
    mappings: dict[str, RepairAction]  # primitive_id → repair
    training_stats: dict

class TransferResults:
    source_verifier: str
    target_verifier: str
    proof_discharge_rates: list[float]
    iterations_per_program: list[int]
    unmapped_rate: float
    syntax_validity_rate: float
```

### 4. EvaluationHarness (`src/evaluation_harness.py`)

**Dependencies:** TransferPipeline, DatasetManager

```python
class EvaluationHarness:
    def __init__(self, pipeline: TransferPipeline, config: dict): ...
    def run_same_tool_baseline(
        self, 
        verifier: str, 
        train: list, 
        test: list
    ) -> BaselineResults: ...
    def run_cross_tool_transfer(
        self, 
        source: str, 
        target: str,
        learned_mappings: LearnedMappings,
        test: list
    ) -> TransferResults: ...
    def run_all_pairs(self, dataset: dict) -> AllPairResults: ...
    def _batch_verify(
        self, 
        verifier: str, 
        programs: list,
        timeout: int = 10
    ) -> list[VerificationResult]: ...

class AllPairResults:
    baseline_results: dict[str, BaselineResults]
    transfer_results: dict[tuple, TransferResults]
    verifier_pairs: list[tuple]
```

### 5. DegradationAnalyzer (`src/degradation_analyzer.py`)

**Dependencies:** scipy, numpy

```python
class DegradationAnalyzer:
    def __init__(self, threshold: float = 20.0): ...
    def compute_degradation(
        self, 
        baseline: float, 
        transfer: float
    ) -> float: ...
    def analyze_all_pairs(
        self, 
        results: AllPairResults
    ) -> DegradationReport: ...
    def test_bidirectionality(
        self, 
        report: DegradationReport
    ) -> BidirectionalityTest: ...
    def statistical_significance(
        self, 
        report: DegradationReport
    ) -> dict: ...

class DegradationReport:
    pair_degradations: dict[tuple, float]
    mean_degradation: float
    gate_passed: bool
    failing_pairs: list[tuple]

class BidirectionalityTest:
    symmetric_pairs: list[tuple]
    asymmetric_pairs: list[tuple]
    max_asymmetry: float
    passed: bool
```

### 6. TransferVisualizer (`src/transfer_visualizer.py`)

**Dependencies:** matplotlib, seaborn, pandas

```python
class TransferVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_transfer_heatmap(
        self, 
        results: AllPairResults, 
        output_path: str
    ): ...
    def plot_degradation_bars(
        self, 
        report: DegradationReport, 
        threshold: float,
        output_path: str
    ): ...
    def plot_convergence_curves(
        self, 
        baseline: list, 
        transfer: list,
        output_path: str
    ): ...
    def plot_coverage_analysis(
        self, 
        normalization_stats: dict,
        output_path: str
    ): ...
```

### 7. DatasetManager (`src/dataset.py`)

**Dependencies:** pathlib, yaml

```python
class DatasetManager:
    def __init__(self, dataset_root: str): ...
    def load_verifier_programs(
        self, 
        verifier: str, 
        split: str = "all"
    ) -> list[Program]: ...
    def create_train_test_split(
        self, 
        verifier: str, 
        ratio: float = 0.8
    ) -> tuple[list, list]: ...
    def validate_programs(
        self, 
        verifier: str, 
        programs: list
    ) -> ValidationReport: ...

class Program:
    id: str
    verifier: str
    source_code: str
    gold_spec: str
    proof_obligations: list[str]
    complexity: dict
```

### 8. MainExperiment (`src/main.py`)

**Dependencies:** All modules

```python
class CrossVerifierExperiment:
    def __init__(self, config_path: str): ...
    def run(self): ...
    def _setup_components(self): ...
    def _run_training_phase(self) -> dict: ...
    def _run_transfer_phase(self, learned: dict) -> AllPairResults: ...
    def _analyze_results(self, results: AllPairResults) -> dict: ...
    def _generate_visualizations(self, results: AllPairResults, stats: dict): ...
    def _write_validation_report(self, results: AllPairResults, stats: dict): ...
```

---

## External Dependencies (Base Hypotheses)

### Module Paths (From h-e2 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| MappingEngine | `from h_e2.src.mapping.mapping_engine import MappingEngine` | `h-e2/code/src/mapping/mapping_engine.py` |
| SemanticPrimitive | `from h_e2.src.data_structures import SemanticPrimitive` | `h-e2/code/src/data_structures.py` |
| ErrorCategory | `from h_e2.src.data_structures import ErrorCategory` | `h-e2/code/src/data_structures.py` |
| Mapping | `from h_e2.src.data_structures import Mapping` | `h-e2/code/src/data_structures.py` |
| CoverageComputer | `from h_e2.src.evaluation.coverage_computer import CoverageComputer` | `h-e2/code/src/evaluation/coverage_computer.py` |

**Verified from:** `h-e2/code/` (actual implementation)

### Module Paths (From h-m1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| IterativeRefinementLoop | `from h_m1.code.src.refinement_loop import IterativeRefinementLoop` | `h-m1/code/code/src/refinement_loop.py` |
| FeedbackExtractor | `from h_m1.code.src.feedback_parser import FeedbackExtractor` | `h-m1/code/code/src/feedback_parser.py` |
| StructuredFeedback | `from h_m1.code.src.feedback_parser import StructuredFeedback` | `h-m1/code/code/src/feedback_parser.py` |
| SpecificationGenerator | `from h_m1.code.src.llm_client import SpecificationGenerator` | `h-m1/code/code/src/llm_client.py` |
| FramaCVerifier | `from h_m1.code.src.verifier import FramaCVerifier` | `h-m1/code/code/src/verifier.py` |
| MetricsTracker | `from h_m1.code.src.metrics import MetricsTracker` | `h-m1/code/code/src/metrics.py` |

**Verified from:** `h-m1/code/` (actual implementation)

---

## Data Flow

### Training Phase (Per Source Verifier)

```
DatasetManager (load 40 programs)
  → IterativeRefinementLoop (run verification)
    → FeedbackExtractor (get raw feedback)
      → CrossVerifierNormalizer (map to universal primitives)
        → TransferPipeline.train (learn primitive→repair mappings)
          → LearnedMappings (store for transfer phase)
```

### Transfer Phase (Per Target Verifier)

```
DatasetManager (load 10 test programs)
  → VerifyWithTarget (get raw feedback from target verifier)
    → CrossVerifierNormalizer (normalize target feedback to same primitives)
      → TransferPipeline.transfer (apply learned source mappings)
        → SyntaxGenerator (generate target-specific syntax)
          → VerifyWithTarget (measure proof discharge)
            → TransferResults (collect metrics)
```

### Analysis Phase

```
AllPairResults (6 transfer pairs)
  → DegradationAnalyzer (compute degradation per pair)
    → DegradationReport (mean degradation, gate check)
      → TransferVisualizer (generate figures)
        → ValidationReportWriter (04_validation.md)
```

---

## File Organization

```
h-m3/
├── config/
│   ├── experiment_config.yaml
│   ├── verifier_configs.yaml
│   └── syntax_templates/
│       ├── frama_c_templates.yaml
│       ├── dafny_templates.yaml
│       └── why3_templates.yaml
├── data/
│   ├── frama_c/
│   │   ├── train/ (40 programs)
│   │   └── test/ (10 programs)
│   ├── dafny/
│   │   ├── train/ (40 programs)
│   │   └── test/ (10 programs)
│   └── why3/
│       ├── train/ (40 programs)
│       └── test/ (10 programs)
├── src/
│   ├── __init__.py
│   ├── normalizer.py
│   ├── syntax_generator.py
│   ├── transfer_pipeline.py
│   ├── evaluation_harness.py
│   ├── degradation_analyzer.py
│   ├── transfer_visualizer.py
│   ├── dataset.py
│   └── main.py
├── results/
│   ├── learned_mappings/
│   ├── metrics.csv
│   ├── degradation.csv
│   └── raw_logs/
├── figures/
│   ├── transfer_heatmap.png
│   ├── degradation_bars.png
│   ├── convergence_curves.png
│   └── coverage_analysis.png
├── main.py
├── requirements.txt
└── README.md
```

---

## Configuration Schema

### experiment_config.yaml

```yaml
experiment:
  name: "h-m3-cross-verifier-transfer"
  hypothesis_id: "h-m3"
  gate_type: "MUST_WORK"
  
taxonomy:
  primitives_path: "../h-e2/results/semantic_primitives.yaml"
  mapping_path: "../h-e2/results/taxonomy_mapping.json"
  coverage_threshold: 0.8

verifiers:
  frama_c:
    version: "28.0"
    command: "frama-c -wp -wp-timeout 10"
    output_parser: "frama_c"
  dafny:
    version: "4.0"
    command: "dafny verify --verification-time-limit:10"
    output_parser: "dafny"
  why3:
    version: "1.6"
    command: "why3 prove --timeout 10"
    output_parser: "why3"

pipeline:
  max_iterations: 10
  timeout_per_run: 10
  no_improvement_threshold: 2
  
llm:
  provider: "anthropic"
  model: "claude-opus-4.5"
  temperature: 0.7
  max_tokens: 4000

evaluation:
  degradation_threshold: 20.0  # %
  bidirectionality_tolerance: 5.0  # pp
  significance_level: 0.05

output:
  results_dir: "results/"
  figures_dir: "figures/"
  log_level: "INFO"
```

### syntax_templates/frama_c_templates.yaml

```yaml
templates:
  - primitive_id: "requires_strengthen"
    template: "/*@ requires {condition}; */"
    examples:
      - "/*@ requires \\valid(arr + (0..n-1)); */"
      - "/*@ requires n > 0; */"
  
  - primitive_id: "ensures_weaken"
    template: "/*@ ensures {postcondition}; */"
    examples:
      - "/*@ ensures \\result == n * (n+1) / 2; */"
  
  - primitive_id: "loop_invariant_add"
    template: "/*@ loop invariant {invariant}; */"
    examples:
      - "/*@ loop invariant 0 <= i <= n; */"
```

---

## Proposed Tasks (Epic Level)

| ID | Task | Description | Complexity | Breakdown | Dependencies |
|----|------|-------------|------------|-----------|--------------|
| T1 | Setup Infrastructure | Project structure, config files, h-e2/h-m1 integration | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) | None |
| T2 | Implement Normalization Layer | CrossVerifierNormalizer with h-e2 taxonomy loading | 12 | Module(3) + Deps(3) + Algo(3) + Integ(3) | T1 |
| T3 | Implement Syntax Generator | Target-specific templates for 3 verifiers | 14 | Module(4) + Deps(2) + Algo(4) + Integ(4) | T1 |
| T4 | Build Transfer Pipeline | Training + transfer logic with normalization injection | 16 | Module(5) + Deps(4) + Algo(4) + Integ(3) | T2, T3 |
| T5 | Dataset Collection | 150 programs (50 per verifier), train/test splits | 11 | Module(3) + Deps(2) + Algo(3) + Integ(3) | T1 |
| T6 | Evaluation Harness | Batch processing for 6 pairs × 10 programs | 13 | Module(4) + Deps(3) + Algo(3) + Integ(3) | T4, T5 |
| T7 | Degradation Analysis | Statistical testing, bidirectionality validation | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) | T6 |
| T8 | Visualization Generation | 4 publication figures (heatmap, bars, curves, coverage) | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) | T7 |
| T9 | Run Experiments | Execute 6 training runs + 6 transfer pairs | 15 | Module(4) + Deps(3) + Algo(4) + Integ(4) | T6 |
| T10 | Validation Report | Gate decision, root cause analysis, 04_validation.md | 10 | Module(3) + Deps(2) + Algo(2) + Integ(3) | T7, T8, T9 |

**Distribution:**  
VeryHigh (18-20): []  
High (14-17): [T3, T4, T9]  
Medium (9-13): [T2, T5, T6, T7, T8, T10]  
Low (4-8): [T1]

**Total Complexity:** 118 (balanced across 10 tasks)

**Critical Path:** T1 → T2 → T4 → T5 → T6 → T9 → T7 → T10

---

## Implementation Notes

### Integration Strategy

1. **h-e2 Reuse**: Load taxonomy_mapping.json as read-only lookup table. No modification to h-e2 code.
2. **h-m1 Extension**: Inject normalization layer between FeedbackExtractor and IterativeRefinementLoop. Minimal changes to h-m1.
3. **New Components**: CrossVerifierNormalizer, SyntaxGenerator, TransferPipeline are h-m3-specific.

### Key Design Decisions

**Normalization Placement**: Apply normalization after h-m1's FeedbackExtractor but before LLM refinement. This preserves h-m1's 3-dimensional feedback structure while abstracting tool-specific details.

**Syntax Generation Strategy**: Template-based with few-shot examples (not learned). LLM generates target syntax using templates + repair action description. Parser validates syntax post-generation.

**Transfer Mechanism**: Store learned mappings as `{primitive_id: repair_action}` dictionary. At transfer time, look up primitive_id from normalized feedback and apply corresponding repair action.

### Risk Mitigation

**Risk 1: Syntax Validity**  
Mitigation: Parser validation after generation. Fallback to manual templates if LLM syntax fails.

**Risk 2: Normalization Coverage**  
Mitigation: Pre-validate h-e2 taxonomy on test programs. Report unmapped_rate in diagnostic metrics.

**Risk 3: Verifier Timeouts**  
Mitigation: 10s timeout per run. Filter dataset to programs that verify <10s with gold specs.

---

## Testing Strategy

### Unit Tests
- `test_normalizer.py`: Verify h-e2 taxonomy loading, mapping lookup
- `test_syntax_generator.py`: Template instantiation, parser validation
- `test_transfer_pipeline.py`: Training/transfer logic with mock verifiers

### Integration Tests
- `test_end_to_end.py`: Frama-C → Dafny transfer on 1 program
- `test_harness.py`: Batch processing, timeout handling

### Validation Tests
- `test_degradation_analyzer.py`: Gate threshold logic, statistical tests
- `test_baseline_parity.py`: Same-tool performance matches h-m1 baseline

---

## Expected Outputs

### Deliverables

1. **Code**: `src/*.py` (8 modules, ~1500 LOC)
2. **Data**: 150 programs, train/test splits, learned_mappings/
3. **Results**: metrics.csv, degradation.csv
4. **Figures**: 4 publication-ready visualizations (PNG, 300dpi)
5. **Report**: 04_validation.md with gate decision

### Success Metrics

**Gate Criteria:**
- Mean degradation ≤20% across 6 pairs
- Bidirectional symmetry: max asymmetry ≤5pp
- Normalization coverage ≥80% per verifier

**Performance Targets:**
- Same-tool baseline: 60-80% (from h-m1)
- Cross-tool with normalization: ≥48% (80% retention)
- Raw transfer (no normalization): ~30-40% (validates necessity)

---

**END OF ARCHITECTURE DOCUMENT**
