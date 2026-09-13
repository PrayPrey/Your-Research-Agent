# Configuration Document: H-C2 Mutation Testing Validation

**Date:** 2026-07-11  
**Hypothesis:** H-C2 - Synthesized specifications achieve ≥70% mutation kill rate relative to gold specs  
**Type:** COMPARISON (Validation of semantic strength)  
**Phase:** Phase 3 Implementation Planning  

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from h-m1 actual code  
**Config Files Found**: h-m1/code/code/src/*.py  
**Pattern Used**: Python dataclass (inheriting from h-m1 patterns)

**Verified Fields from Base Code**:
- `SpecificationGenerator`: model="claude-opus-4-5", api_key from environment
- `FramaCVerifier`: timeout_per_obligation=10, provers=["alt-ergo", "z3"]
- `IterativeRefinementLoop`: max_iterations=10, no_improvement_threshold=3
- `ACSLSpec`: annotated_code, preconditions, postconditions, loop_invariants, assertions
- `StructuredFeedback`: witness, structure, dependency, natural_language

---

## Configuration Overview

**Applied**: Mutation testing framework pattern with controlled comparison (from Archon KB)

This comparison study reuses h-m1 specification synthesis mechanism (FullStructured feedback) and adds mutation testing to validate semantic strength. All synthesis parameters match h-m1 validated settings.

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-m1/code/code/src/llm_client.py (ACTUAL CODE)
@dataclass
class ACSLSpec:
    annotated_code: str
    preconditions: List[str]
    postconditions: List[str]
    loop_invariants: List[str]
    assertions: List[str]

class SpecificationGenerator:
    def __init__(self, api_key: str, model: str = "claude-opus-4-5"):
        self.model = model
        self.client = Anthropic(api_key=api_key)

# From: h-m1/code/code/src/verifier.py (ACTUAL CODE)
@dataclass
class VerificationResult:
    total_obligations: int
    proved_obligations: int
    failed_obligations: int
    proof_discharge_rate: float
    obligations: List[ProofObligation]
    raw_output: str

class FramaCVerifier:
    def __init__(
        self,
        timeout_per_obligation: int = 10,
        provers: List[str] = None
    ):
        self.timeout = timeout_per_obligation
        self.provers = provers or ["alt-ergo", "z3"]

# From: h-m1/code/code/src/refinement_loop.py (ACTUAL CODE)
class IterativeRefinementLoop:
    def __init__(
        self,
        generator: SpecificationGenerator,
        verifier: FramaCVerifier,
        feedback_extractor: FeedbackExtractor,
        max_iterations: int = 10,
        no_improvement_threshold: int = 3
    ):
        self.max_iterations = max_iterations
        self.no_improvement_threshold = no_improvement_threshold

# From: h-m1/code/code/src/feedback_parser.py (ACTUAL CODE)
@dataclass
class StructuredFeedback:
    witness: WitnessInstantiation
    structure: LogicalStructure
    dependency: DependencyPreservation
    natural_language: str
```

**Verified from**: `/workspace/TEST_verifai/docs/youra_research/h-m1/code/code/` (actual implementation)

---

## C-1: Mutation Operators [Complexity: 14, Budget: 4]

**Applied**: AST-based mutation pattern from PyTorch inductor config

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from enum import Enum
from typing import List

class MutationOperatorType(Enum):
    ARITHMETIC = "arithmetic"
    RELATIONAL = "relational"
    BOOLEAN = "boolean"
    STATEMENT = "statement"
    BOUNDARY = "boundary"

@dataclass
class MutationOperatorConfig:
    operators_enabled: List[str] = field(default_factory=lambda: [
        "ADD_TO_SUB", "SUB_TO_ADD", "MUL_TO_DIV",
        "LT_TO_LEQ", "GT_TO_GEQ", "EQ_TO_NEQ",
        "AND_TO_OR", "OR_TO_AND", "NEGATE_COND",
        "DELETE_STMT", "CHANGE_CONST",
        "ARRAY_OFF_BY_ONE", "LOOP_BOUND_SHIFT"
    ])
    filter_non_compilable: bool = True
    use_ast_parsing: bool = True  # pycparser-based
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Arithmetic Operators | Implement +/-, *//, ++/-- mutations (3 complexity) |
| C-1-2 | Relational/Boolean Operators | Implement </<=/>, &&/\|\|, ! mutations (4 complexity) |
| C-1-3 | Statement/Boundary Operators | Implement delete, const change, off-by-one (4 complexity) |
| C-1-4 | Compilability Filter | AST validation and filtering (3 complexity) |

---

## C-2: Mutant Generator [Complexity: 11, Budget: 3]

**Applied**: Standard PyTorch/pycparser AST traversal patterns

### Configuration (Python Dataclass)

```python
@dataclass
class MutantGeneratorConfig:
    parser: str = "pycparser"
    parallel_generation: bool = True
    max_mutants_per_program: int = 100
    deduplicate_mutants: bool = True
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | AST Parser Integration | Integrate pycparser for C AST (3 complexity) |
| C-2-2 | Mutant Application | Apply operators to AST nodes (4 complexity) |
| C-2-3 | Filtering & Deduplication | Remove duplicates and non-compilable (4 complexity) |

---

## C-3: Mutation Tester [Complexity: 13, Budget: 3]

**Applied**: Parallel testing pattern with timeout handling

### Configuration (Python Dataclass)

```python
@dataclass
class MutationTesterConfig:
    # Inherited from h-m1
    verifier_timeout: int = 10  # seconds per mutant
    provers: List[str] = field(default_factory=lambda: ["alt-ergo", "z3", "cvc5"])
    
    # Mutation-specific
    parallel_workers: int = 4
    mutant_timeout_multiplier: float = 1.0  # Keep same as h-m1
    
    # Classification
    killed_on_verification_failed: bool = True  # Mutant killed if WP fails
    survived_on_verification_passed: bool = True
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | Verification Integration | Run Frama-C/WP on (mutant, spec) pairs (4 complexity) |
| C-3-2 | Parallel Execution | Multi-worker mutant testing (4 complexity) |
| C-3-3 | Result Aggregation | Compute kill rates and breakdown (5 complexity) |

---

## C-4: Specification Synthesizer [Complexity: 7, Budget: 2]

**Applied**: Direct h-m1 reuse pattern

### Configuration (Python Dataclass)

```python
@dataclass
class SpecSynthesizerConfig:
    # INHERITED FROM H-M1 (no changes)
    llm_model: str = "claude-opus-4-5"
    llm_temperature: float = 0.0  # Deterministic for reproducibility
    max_iterations: int = 10
    no_improvement_threshold: int = 3
    feedback_type: str = "FullStructured"  # Validated in h-m1
    
    # API
    api_key_env: str = "ANTHROPIC_API_KEY"
    retry_attempts: int = 3
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | H-M1 Integration | Import and wrap IterativeRefinementLoop (4 complexity) |
| C-4-2 | Synthesis Runner | Run synthesis for 30 programs with checkpointing (3 complexity) |

---

## C-5: Dataset Loader [Complexity: 8, Budget: 2]

**Applied**: Standard dataset loading pattern

### Configuration (Python Dataclass)

```python
@dataclass
class DatasetLoaderConfig:
    repository_url: str = "https://github.com/fraunhoferfokus/acsl-by-example"
    cache_dir: str = ".cache/datasets/acsl-by-example"
    
    # Selection criteria
    num_programs: int = 30
    stratified_sampling: bool = True
    
    # Filters
    loc_range: Tuple[int, int] = (10, 100)
    proof_obligations_range: Tuple[int, int] = (5, 20)
    
    # Preprocessing
    strip_acsl_annotations: bool = True  # For synthesis
    preserve_gold_specs: bool = True  # For comparison
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Repository Cloning & Parsing | Clone repo, parse C files and ACSL (4 complexity) |
| C-5-2 | Stratified Sampling | Select diverse 30 programs by complexity (4 complexity) |

---

## C-6: Comparison Analyzer [Complexity: 12, Budget: 3]

**Applied**: Statistical comparison pattern

### Configuration (Python Dataclass)

```python
@dataclass
class ComparisonAnalyzerConfig:
    gate_threshold: float = 0.70  # Synthesized ≥ 70% of gold
    significance_level: float = 0.05
    
    # Comparison metrics
    primary_metric: str = "kill_rate"
    secondary_metrics: List[str] = field(default_factory=lambda: [
        "operator_coverage",
        "timeout_rate",
        "mutation_diversity"
    ])
    
    # Gate logic
    gate_type: str = "MUST_WORK"
    gate_formula: str = "mean_synthesized >= 0.70 * mean_gold"
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Kill Rate Comparison | Compute synthesized vs gold per program (4 complexity) |
| C-6-2 | Gate Decision Logic | Evaluate gate threshold and generate decision (4 complexity) |
| C-6-3 | Statistical Breakdown | Operator effectiveness, program complexity analysis (4 complexity) |

---

## C-7: Mutation Visualizer [Complexity: 11, Budget: 3]

**Applied**: Standard matplotlib/seaborn visualization patterns

### Configuration (Python Dataclass)

```python
@dataclass
class MutationVisualizerConfig:
    output_dir: str = "docs/youra_research/h-c2/figures"
    dpi: int = 300
    format: str = "png"
    
    # Required plots
    required_figures: List[str] = field(default_factory=lambda: [
        "gate_comparison",
        "kill_rate_distribution",
        "operator_effectiveness",
        "strength_vs_discharge",
        "complexity_vs_kill_rate"
    ])
    
    # Styling
    color_synthesized: str = "#3498db"
    color_gold: str = "#2ecc71"
    confidence_level: float = 0.95
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Gate Comparison Plot | Bar chart: synthesized vs gold kill rates (4 complexity) |
| C-7-2 | Distribution & Operator Plots | Histogram and operator breakdown (4 complexity) |
| C-7-3 | Correlation Plots | Strength vs discharge, complexity analysis (3 complexity) |

---

## C-8: Validation Reporter [Complexity: 8, Budget: 2]

**Applied**: Standard validation report generation pattern

### Configuration (Python Dataclass)

```python
@dataclass
class ValidationReporterConfig:
    hypothesis_folder: str = "docs/youra_research/h-c2"
    validation_report_filename: str = "04_validation.md"
    verification_state_file: str = "../../verification_state.yaml"
    
    # Report sections
    include_sections: List[str] = field(default_factory=lambda: [
        "experiment_configuration",
        "dataset_summary",
        "mutation_operator_statistics",
        "per_program_kill_rates",
        "gate_decision",
        "figure_references"
    ])
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Report Generation | Generate 04_validation.md from results (4 complexity) |
| C-8-2 | State Update | Update verification_state.yaml with gate decision (4 complexity) |

---

## C-9: Integration Runner [Complexity: 15, Budget: 4]

**Applied**: End-to-end pipeline orchestration pattern

### Configuration (Python Dataclass)

```python
@dataclass
class MutationExperimentConfig:
    # Experiment metadata
    experiment_name: str = "h-c2-mutation-testing"
    hypothesis_type: str = "COMPARISON"
    gate_type: str = "MUST_WORK"
    
    # Paths
    hypothesis_folder: Path = Path("docs/youra_research/h-c2")
    output_dir: Path = Path("docs/youra_research/h-c2/results")
    checkpoint_dir: Path = Path("docs/youra_research/h-c2/checkpoints")
    
    # Component configs (composed)
    dataset: DatasetLoaderConfig = field(default_factory=DatasetLoaderConfig)
    mutation_operators: MutationOperatorConfig = field(default_factory=MutationOperatorConfig)
    mutant_generator: MutantGeneratorConfig = field(default_factory=MutantGeneratorConfig)
    mutation_tester: MutationTesterConfig = field(default_factory=MutationTesterConfig)
    synthesizer: SpecSynthesizerConfig = field(default_factory=SpecSynthesizerConfig)
    comparison: ComparisonAnalyzerConfig = field(default_factory=ComparisonAnalyzerConfig)
    visualization: MutationVisualizerConfig = field(default_factory=MutationVisualizerConfig)
    reporter: ValidationReporterConfig = field(default_factory=ValidationReporterConfig)
    
    # Checkpointing
    checkpoint_interval: int = 5  # Save every 5 programs
    resume_from_checkpoint: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "docs/youra_research/h-c2/logs/experiment.log"
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Pipeline Orchestration | Sequential execution: load → synthesize → mutate → compare (4 complexity) |
| C-9-2 | Checkpointing & Recovery | Save/resume at program-level granularity (4 complexity) |
| C-9-3 | Error Handling | Graceful failure handling, retry logic (3 complexity) |
| C-9-4 | Results Aggregation | Collect all outputs, generate final report (4 complexity) |

---

## Configuration Rationale

### Non-Standard Values

**llm_temperature: 0.0** (vs 0.7 in h-m1 initial generation)
- Deterministic synthesis required for reproducible comparison
- Matches h-m1 validation settings for consistency

**num_programs: 30** (vs 10 in h-e1)
- Statistical power requirement for comparison study
- Sufficient for detecting 10pp difference at 80% power

**checkpoint_interval: 5** (vs 10 in h-m1)
- Program-level granularity for mutation testing (expensive)
- 5 programs = ~150 mutants × 2 specs = ~300 verifications per checkpoint

**parallel_workers: 4** (vs single-threaded in h-m1)
- Mutation testing is embarrassingly parallel (independent mutants)
- 4 workers reduces 5-hour runtime to ~1.5 hours

---

## Summary

This configuration provides **copy-paste ready** mutation testing setup for H-C2:

1. **Inherits h-m1 synthesis configs** (SpecificationGenerator, IterativeRefinementLoop, FramaCVerifier)
2. **Adds mutation-specific configs** (12 operators, parallel testing, kill rate computation)
3. **Per-task dataclasses** for all 9 Epic tasks
4. **Gate logic**: synthesized_kill_rate ≥ 0.70 × gold_kill_rate
5. **Resource estimate**: 30 programs × 2 specs × ~30 mutants = ~1800 verifications (~1.5 hours with 4 workers)

**Phase 4 Coder**: Use dataclass configs as-is. All synthesis parameters match h-m1 validated settings. Focus implementation on mutation operators and kill rate computation.

**Key Difference from h-m1**: This is a COMPARISON hypothesis testing semantic strength via mutation, not a MECHANISM ablation. No hyperparameter variations—fixed h-m1 synthesis + new mutation testing layer.

**Reproducibility**: Deterministic synthesis (temp=0.0), same verifier settings (10s timeout, alt-ergo/z3/cvc5), program-level checkpointing for resume.
