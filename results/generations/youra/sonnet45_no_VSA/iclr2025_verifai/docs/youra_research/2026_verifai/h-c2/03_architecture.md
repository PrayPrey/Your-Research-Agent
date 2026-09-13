# System Architecture: H-C2 Mutation Testing for Specification Non-Vacuity

**Date:** 2026-07-11  
**Hypothesis:** H-C2 - Synthesized specifications achieve ≥70% mutation kill rate relative to expert-written gold specs  
**PRD:** 03_prd.md  
**Experiment Brief:** 02c_experiment_brief.md  
**Architecture Type:** COMPARISON - Validation of semantic strength via mutation testing

---

## Knowledge Base Application

Applied: Standard mutation testing framework patterns, test oracle design

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from h-m1 base code  
**Analyzed Path:** `docs/youra_research/h-m1/code/code/`  
**Findings:** Refinement loop architecture verified. Module structure uses relative imports (`from .llm_client import`). StructuredFeedback mechanism available for reuse.

---

## System Context

### Core Hypothesis Test

**Question:** Do synthesized ACSL specifications detect semantic bugs (non-vacuous)?

**Mechanism:** Mutation Testing - Generate code mutants, verify if specifications detect them (kill rate).

**Success Criteria:**
1. Synthesized specs achieve ≥70% of gold spec kill rate
2. Successfully process 30+ programs from ACSL-by-Example
3. Automated pipeline: synthesis → mutation → verification → metrics

### System Boundaries

**Input:** 30 C programs with gold ACSL specifications (ACSL-by-Example benchmark)  
**Output:** Per-spec kill rates + gate decision + comparison figures  
**External Dependencies:**
- Base h-m1 code (specification synthesis mechanism)
- Anthropic API (Claude Opus)
- Frama-C 32.0 + WP + solvers (Alt-Ergo, Z3, CVC5)
- ACSL-by-Example dataset

**Out of Scope:**
- Specification mutation (mutate code, not specs)
- Multi-model comparison (single LLM only)
- Real-world bug detection (controlled mutation testing only)

---

## Module Structure

### 1. MutationOperator (`src/mutation_operators.py`)

**Dependencies:** pycparser (C AST parsing)

```python
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass

class MutationOperator(ABC):
    @abstractmethod
    def apply(self, ast: CAST) -> List[Mutant]: ...
    def get_operator_name(self) -> str: ...

class ArithmeticMutation(MutationOperator):
    def apply(self, ast: CAST) -> List[Mutant]: ...

class RelationalMutation(MutationOperator):
    def apply(self, ast: CAST) -> List[Mutant]: ...

class BooleanMutation(MutationOperator):
    def apply(self, ast: CAST) -> List[Mutant]: ...

class StatementMutation(MutationOperator):
    def apply(self, ast: CAST) -> List[Mutant]: ...

class BoundaryMutation(MutationOperator):
    def apply(self, ast: CAST) -> List[Mutant]: ...

@dataclass
class Mutant:
    mutant_id: str
    original_code: str
    mutated_code: str
    operator_type: str
    location: dict
```

### 2. MutantGenerator (`src/mutant_generator.py`)

**Dependencies:** mutation_operators, pycparser

```python
class MutantGenerator:
    def __init__(self, operators: List[MutationOperator]): ...
    def generate_mutants(self, c_program: str) -> List[Mutant]: ...
    def filter_compilable(self, mutants: List[Mutant]) -> List[Mutant]: ...
    def count_by_operator(self, mutants: List[Mutant]) -> dict: ...

class CASTParser:
    def parse(self, c_code: str) -> CAST: ...
    def unparse(self, ast: CAST) -> str: ...
    def check_compilability(self, c_code: str) -> bool: ...
```

### 3. MutationTester (`src/mutation_tester.py`)

**Dependencies:** mutant_generator, h-m1 verifier

```python
from dataclasses import dataclass
from typing import List

@dataclass
class MutationTestResult:
    mutant_id: str
    killed: bool
    verification_status: str
    timeout: bool
    error: Optional[str]

@dataclass
class KillRateResult:
    program_id: str
    spec_type: str
    total_mutants: int
    killed: int
    survived: int
    timeout_count: int
    kill_rate: float
    operator_breakdown: dict

class MutationTester:
    def __init__(self, verifier, timeout: int = 10): ...
    def test_mutant(self, mutant: Mutant, acsl_spec) -> MutationTestResult: ...
    def compute_kill_rate(self, program: Program, spec: ACSLSpec) -> KillRateResult: ...
    def run_parallel(self, mutants: List[Mutant], spec: ACSLSpec, workers: int = 4) -> List[MutationTestResult]: ...
```

### 4. SpecificationSynthesizer (`src/spec_synthesizer.py`)

**Dependencies:** h-m1 refinement loop

```python
class SpecificationSynthesizer:
    def __init__(self, llm_client, verifier, feedback_extractor): ...
    def synthesize_with_feedback(self, c_program: str, max_iterations: int = 10) -> ACSLSpec: ...
    def get_synthesis_metrics(self) -> dict: ...
```

### 5. DatasetLoader (`src/dataset_loader.py`)

**Dependencies:** git, yaml

```python
from dataclasses import dataclass
from typing import List

@dataclass
class Program:
    program_id: str
    c_code: str
    gold_spec: ACSLSpec
    loc: int
    function_count: int
    complexity: str
    file_path: str

class ACSLByExampleLoader:
    def __init__(self, repo_path: str): ...
    def load_programs(self, num_programs: int = 30, stratified: bool = True) -> List[Program]: ...
    def get_program_metadata(self, program: Program) -> dict: ...
    def validate_gold_spec(self, program: Program) -> bool: ...
```

### 6. ComparisonAnalyzer (`src/comparison_analyzer.py`)

**Dependencies:** scipy, numpy

```python
from dataclasses import dataclass

@dataclass
class ComparisonResult:
    program_id: str
    synthesized_kill_rate: float
    gold_kill_rate: float
    relative_performance: float
    synthesized_result: KillRateResult
    gold_result: KillRateResult

@dataclass
class GateDecision:
    gate_passed: bool
    mean_synthesized: float
    mean_gold: float
    threshold: float
    relative_performance: float
    failing_programs: List[str]

class ComparisonAnalyzer:
    def __init__(self, threshold: float = 0.70): ...
    def compare_specs(self, synthesized_results: List[KillRateResult], gold_results: List[KillRateResult]) -> List[ComparisonResult]: ...
    def compute_gate_decision(self, comparisons: List[ComparisonResult]) -> GateDecision: ...
    def generate_statistics(self, comparisons: List[ComparisonResult]) -> dict: ...
```

### 7. MutationVisualizer (`src/mutation_visualizer.py`)

**Dependencies:** matplotlib, seaborn

```python
class MutationVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_kill_rate_comparison(self, comparisons: List[ComparisonResult], output_path: str): ...
    def plot_kill_rate_distribution(self, results: List[KillRateResult], output_path: str): ...
    def plot_operator_effectiveness(self, results: List[KillRateResult], output_path: str): ...
    def plot_strength_vs_discharge(self, results: List[KillRateResult], discharge_data: dict, output_path: str): ...
    def plot_complexity_analysis(self, results: List[KillRateResult], programs: List[Program], output_path: str): ...
    def generate_all_figures(self, comparisons: List[ComparisonResult], programs: List[Program]): ...
```

### 8. ValidationReporter (`src/validation_reporter.py`)

**Dependencies:** yaml

```python
class ValidationReporter:
    def __init__(self, hypothesis_folder: str): ...
    def generate_validation_report(self, gate_decision: GateDecision, comparisons: List[ComparisonResult], stats: dict) -> str: ...
    def update_verification_state(self, gate_decision: GateDecision): ...
    def save_checkpoint(self, results: dict, checkpoint_name: str): ...
    def load_checkpoint(self, checkpoint_name: str) -> dict: ...
```

### 9. MutationExperimentRunner (`src/main_mutation.py`)

**Dependencies:** All modules

```python
class MutationExperimentRunner:
    def __init__(self, config_path: str): ...
    def run(self): ...
    def _setup_components(self): ...
    def _load_dataset(self) -> List[Program]: ...
    def _synthesize_specifications(self, programs: List[Program]) -> List[ACSLSpec]: ...
    def _run_mutation_testing(self, programs: List[Program], specs: List[ACSLSpec]) -> tuple: ...
    def _analyze_results(self, synthesized_results: List[KillRateResult], gold_results: List[KillRateResult]) -> GateDecision: ...
    def _generate_outputs(self, gate_decision: GateDecision, comparisons: List[ComparisonResult]): ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-m1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| SpecificationGenerator | `from h_m1.code.code.src.llm_client import SpecificationGenerator` | `h-m1/code/code/src/llm_client.py` |
| FramaCVerifier | `from h_m1.code.code.src.verifier import FramaCVerifier` | `h-m1/code/code/src/verifier.py` |
| FeedbackExtractor | `from h_m1.code.code.src.feedback_parser import FeedbackExtractor` | `h-m1/code/code/src/feedback_parser.py` |
| IterativeRefinementLoop | `from h_m1.code.code.src.refinement_loop import IterativeRefinementLoop` | `h-m1/code/code/src/refinement_loop.py` |
| ACSLSpec | `from h_m1.code.code.src.llm_client import ACSLSpec` | `h-m1/code/code/src/llm_client.py` |
| VerificationResult | `from h_m1.code.code.src.verifier import VerificationResult` | `h-m1/code/code/src/verifier.py` |
| StructuredFeedback | `from h_m1.code.code.src.feedback_parser import StructuredFeedback` | `h-m1/code/code/src/feedback_parser.py` |

**Verified from:** `docs/youra_research/h-m1/code/code/` (actual implementation)

**Note:** h-m1 uses nested `code/code/` structure. Import paths must reflect actual directory layout.

---

## Data Flow

### End-to-End Pipeline

```
DatasetLoader → Programs (30)
                    ↓
          SpecificationSynthesizer → Synthesized Specs
                    ↓
          MutantGenerator → Mutants per Program
                    ↓
    [For each (Program, Spec) pair: Synthesized + Gold]
                    ↓
          MutationTester → KillRateResults
                    ↓
          ComparisonAnalyzer → GateDecision
                    ↓
          MutationVisualizer + ValidationReporter → Outputs
```

### Mutation Testing Flow (Per Program)

**Step 1: Mutant Generation**
1. Parse C program to AST (pycparser)
2. Apply 12 mutation operators
3. Filter out non-compilable mutants
4. Return List[Mutant]

**Step 2: Specification Synthesis** (Synthesized specs only)
1. Load C program
2. Run IterativeRefinementLoop (from h-m1) with FullStructured feedback
3. Return synthesized ACSLSpec

**Step 3: Mutation Testing**
1. For each mutant:
   - Insert ACSL annotations (spec) into mutant code
   - Run Frama-C/WP verification (10s timeout)
   - Record: Killed (verification failed) | Survived (verification passed)
2. Compute kill_rate = (killed / total) × 100%

**Step 4: Comparison Analysis**
1. Compare synthesized_kill_rate vs gold_kill_rate per program
2. Check gate: mean(synthesized) ≥ 0.70 × mean(gold)
3. Generate statistics and breakdown

**Step 5: Reporting**
1. Generate validation report (04_validation.md)
2. Generate 5 required figures
3. Update verification_state.yaml

---

## File Organization

```
h-c2/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── mutation_operators.py       # NEW - 12 mutation operators
│   │   ├── mutant_generator.py         # NEW - AST-based mutant generation
│   │   ├── mutation_tester.py          # NEW - Kill rate computation
│   │   ├── spec_synthesizer.py         # NEW - Wraps h-m1 refinement
│   │   ├── dataset_loader.py           # NEW - ACSL-by-Example loader
│   │   ├── comparison_analyzer.py      # NEW - Gate decision logic
│   │   ├── mutation_visualizer.py      # NEW - 5 plots
│   │   ├── validation_reporter.py      # NEW - Report generation
│   │   └── main_mutation.py            # NEW - Entry point
│   ├── config/
│   │   └── mutation_config.yaml        # Experiment configuration
│   ├── requirements.txt                # pycparser, scipy, h-m1 deps
│   └── run_mutation_experiment.py      # Entry point
├── data/
│   └── acsl-by-example/                # Cloned dataset (30 programs)
├── results/
│   ├── synthesized_specs/              # Per-program synthesized specs
│   ├── mutation_results/               # Per-program kill rates
│   │   ├── program_001_synthesized.json
│   │   ├── program_001_gold.json
│   │   └── ...
│   ├── checkpoints/
│   │   ├── synthesized_specs.json      # Resume synthesis
│   │   └── mutation_results.json       # Resume testing
│   └── experiment_log.md               # Human-readable log
├── figures/
│   ├── gate_comparison.png             # Required gate plot
│   ├── kill_rate_distribution.png
│   ├── operator_effectiveness.png
│   ├── strength_vs_discharge.png
│   └── complexity_vs_kill_rate.png
└── 04_validation.md                    # Results report (Phase 4 output)
```

---

## Configuration Management

### Mutation Config (`config/mutation_config.yaml`)

```yaml
# Dataset
dataset:
  name: "acsl-by-example"
  repo_url: "https://github.com/fraunhoferfokus/acsl-by-example"
  num_programs: 30
  stratified_sampling: true
  selection_criteria:
    loc_range: [10, 100]
    proof_obligations_range: [5, 20]

# Mutation Operators (12 total)
mutation:
  operators:
    arithmetic: ["ADD_TO_SUB", "MUL_TO_DIV", "INC_TO_DEC"]
    relational: ["LT_TO_LEQ", "GT_TO_GEQ", "EQ_TO_NEQ"]
    boolean: ["AND_TO_OR", "NEGATE_COND"]
    statement: ["DELETE_STMT", "CHANGE_CONST"]
    boundary: ["ARRAY_OFF_BY_ONE", "LOOP_BOUND_SHIFT"]
  filter_non_compilable: true
  parallel_workers: 4

# Specification Synthesis (from h-m1)
synthesis:
  llm_model: "claude-opus-4-8"
  temperature: 0.0
  max_iterations: 10
  feedback_type: "FullStructured"
  api_key_env: "ANTHROPIC_API_KEY"

# Verification
verification:
  frama_c_version: "32.0"
  timeout_seconds: 10
  provers: ["alt-ergo", "z3", "cvc5"]
  parallel_provers: true

# Comparison
comparison:
  gate_threshold: 0.70
  significance_level: 0.05

# Output
output:
  figures_dir: "figures"
  results_dir: "results"
  checkpoint_interval: 5
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Mutation Operators | Implement 12 AST-based mutation operators for C code | 14 | operator logic(5) + AST traversal(4) + compilability check(3) + testing(2) |
| C-2 | Mutant Generator | Generate and filter compilable mutants from C programs | 11 | AST parsing(3) + operator application(3) + filtering(3) + parallel generation(2) |
| C-3 | Mutation Tester | Execute mutants with Frama-C and compute kill rates | 13 | verification integration(4) + parallel execution(3) + timeout handling(3) + result aggregation(3) |
| C-4 | Specification Synthesizer | Wrap h-m1 refinement loop for ACSL synthesis | 7 | h-m1 integration(3) + API client setup(2) + error handling(2) |
| C-5 | Dataset Loader | Clone and load ACSL-by-Example benchmark programs | 8 | git operations(2) + program parsing(3) + stratified sampling(2) + validation(1) |
| C-6 | Comparison Analyzer | Compare synthesized vs gold specs and make gate decision | 12 | kill rate comparison(4) + gate logic(3) + statistical tests(3) + breakdown analysis(2) |
| C-7 | Mutation Visualizer | Generate 5 required plots for mutation testing results | 11 | gate comparison plot(3) + distribution plots(3) + scatter plots(3) + operator breakdown(2) |
| C-8 | Validation Reporter | Auto-generate 04_validation.md and update state | 8 | report template(3) + state update(2) + checkpoint management(2) + markdown(1) |
| C-9 | Integration Runner | End-to-end pipeline orchestration with checkpointing | 15 | orchestration(5) + checkpoint recovery(3) + error handling(3) + logging(2) + parallel coordination(2) |

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): [C-1, C-9]
- Medium (9-13): [C-2, C-3, C-6, C-7]
- Low (4-8): [C-4, C-5, C-8]

**Total Complexity:** 99 points (9 tasks)

---

## Critical Design Decisions

### 1. Mutate Code, Not Specifications

**Decision:** Apply mutation operators to C code, test if specs detect mutants.

**Rationale:**
- Specification mutation requires ACSL-specific operators (complex)
- Code mutation is standard practice in mutation testing literature
- Kill rate directly measures specification strength (test oracle quality)

**Implementation:**
```python
# Apply mutation to C code
mutant = mutate_c_code(original_program, operator)

# Test if specification detects it
annotated = insert_acsl_spec(mutant, synthesized_spec)
result = frama_c_wp_verify(annotated, timeout=10)

# Killed = spec detected the bug
killed = (result.status == "VERIFICATION_FAILED")
```

### 2. Reuse h-m1 Synthesis Mechanism

**Decision:** Import IterativeRefinementLoop from h-m1 for specification synthesis.

**Rationale:**
- h-m1 validated FullStructured feedback as best-performing
- Reuse ensures consistency with validated mechanism
- No need to reimplement synthesis logic

**Implementation:**
```python
from h_m1.code.code.src.refinement_loop import IterativeRefinementLoop

# Use validated synthesis mechanism
synthesizer = IterativeRefinementLoop(generator, verifier, feedback_extractor)
synthesized_spec = synthesizer.synthesize(c_program)
```

### 3. Parallel Mutation Testing

**Decision:** Run mutant verification in parallel (4 workers).

**Rationale:**
- 30 programs × ~30 mutants/program × 2 specs = ~1800 verifications
- 10s timeout × 1800 = 5 hours serial
- Parallel execution reduces to ~1.5 hours

**Implementation:**
```python
from multiprocessing import Pool

with Pool(workers=4) as pool:
    results = pool.starmap(verify_mutant, [(m, spec) for m in mutants])
```

### 4. Checkpoint at Program Level

**Decision:** Save results after each program completes (synthesis + mutation testing).

**Rationale:**
- Program-level granularity allows resume on failure
- Synthesis checkpoints enable skipping completed programs
- Mutation results checkpointed separately

---

## Validation Strategy

### Unit Tests

**Test Coverage:**
- MutationOperator: Test each operator with synthetic C AST
- MutantGenerator: Test mutant generation with small C programs
- MutationTester: Mock Frama-C verification, test kill rate computation
- ComparisonAnalyzer: Test gate decision logic with synthetic data

### Integration Tests

**End-to-End Test:**
1. 3 programs × 2 specs (synthesized + gold) = 6 kill rate computations
2. Expected: All tests complete, gate decision made, plots generated
3. Verify: Kill rates computed correctly, comparison logic works

### Validation Criteria (Phase 4)

**Code Validation:**
- All unit tests pass
- Imports from h-m1 resolve correctly
- No hardcoded API keys or paths

**Experiment Validation:**
- Gate comparison plot generated
- Kill rate comparison produces valid result
- 04_validation.md contains gate decision

---

**Architecture Version:** 1.0  
**Status:** Ready for Phase 4 Implementation  
**Next Step:** Phase 4 Coder implements modules following this specification
