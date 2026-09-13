# System Architecture: H-M2 Staged Progressive Refinement

**Date:** 2026-07-11  
**Hypothesis:** H-M2 - Staged progressive refinement (types→pre→post→inv) converges faster and achieves higher proof discharge than complete upfront specification  
**PRD:** 03_prd.md  
**Experiment Brief:** 02c_experiment_brief.md  
**Architecture Type:** MECHANISM (Comparison) - Staged vs Complete strategies  

---

## Knowledge Base Application

Applied: Iterative refinement patterns, two-stage refinement architecture (base + refiner)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Patterns found from base code (h-e1)  
**Analyzed Path**: docs/youra_research/h-e1/code/  
**Findings**: H-E1 implements Complete strategy (all components simultaneously). Module structure: LLMClient (generation/refinement), FramaCVerifier, FeedbackParser, RefinementLoop. Reusing verifier and feedback infrastructure, extending refinement logic for staged approach.

---

## System Context

### Core Hypothesis Test

**Question:** Does staged progressive refinement (types→pre→post→inv) converge faster and achieve higher proof discharge than complete upfront specification?

**Mechanism:** Sequential specification synthesis through 4 stages vs. simultaneous generation of all components.

**Success Criteria:**
- Staged converges in ≤70% of iterations vs Complete
- Staged achieves ≥5pp higher final proof discharge rate
- Statistical significance (p < 0.05, paired t-test)

### System Boundaries

**Input:** 30-50 C programs from ACSL by Example benchmark (unannotated)  
**Output:** Comparison metrics (convergence speed, discharge rate, stage improvements, backtracking events) + statistical analysis  
**External Dependencies:** Inherits from H-E1 (LLM client, Frama-C verifier)

**Out of Scope:**
- Proof-aware decomposition (AutoSpec+ Stage 1)
- Termination analysis
- Multi-program call graph analysis

---

## Module Structure

### 1. StagedRefinementStrategy (`src/staged_strategy.py`)

**Dependencies:** llm_client (h-e1), verifier (h-e1), feedback_parser (h-e1)

```python
class StagedRefinementStrategy:
    def __init__(self, generator: SpecificationGenerator, verifier: FramaCVerifier, feedback_extractor: FeedbackExtractor, max_iter_per_stage: int = 3): ...
    def synthesize_specification(self, c_code: str, program_id: str) -> StagedResult: ...
    def refine_stage(self, c_code: str, spec_so_far: PartialSpec, stage: StageType, max_iter: int) -> StageResult: ...
    def _build_stage_prompt(self, c_code: str, spec_so_far: PartialSpec, stage: StageType) -> str: ...
    def _verify_partial(self, c_code: str, partial_spec: PartialSpec, stage: StageType) -> VerificationResult: ...

class StageType(Enum):
    TYPES = "types"
    PRECONDITIONS = "preconditions"
    POSTCONDITIONS = "postconditions"
    INVARIANTS = "invariants"

class PartialSpec:
    types: str
    preconditions: str
    postconditions: str
    invariants: str

class StageResult:
    spec_component: str
    iterations: int
    discharge_rate: float
    converged: bool

class StagedResult:
    final_spec: ACSLSpec
    total_iterations: int
    stage_history: dict[StageType, StageResult]
    backtracking_events: int
    convergence_reason: ConvergenceReason
```

### 2. CompleteRefinementStrategy (`src/complete_strategy.py`)

**Dependencies:** llm_client (h-e1), verifier (h-e1), feedback_parser (h-e1)

```python
class CompleteRefinementStrategy:
    def __init__(self, generator: SpecificationGenerator, verifier: FramaCVerifier, feedback_extractor: FeedbackExtractor, max_iterations: int = 10): ...
    def synthesize_specification(self, c_code: str, program_id: str) -> CompleteResult: ...
    def _generate_complete_spec(self, c_code: str, previous_spec: Optional[ACSLSpec], feedback: Optional[StructuredFeedback]) -> ACSLSpec: ...
    def _check_convergence(self, discharge_history: list[float]) -> bool: ...

class CompleteResult:
    final_spec: ACSLSpec
    total_iterations: int
    discharge_history: list[float]
    converged: bool
    convergence_reason: ConvergenceReason
```

### 3. ComparisonExperiment (`src/comparison_experiment.py`)

**Dependencies:** StagedRefinementStrategy, CompleteRefinementStrategy, dataset (h-e1)

```python
class ComparisonExperiment:
    def __init__(self, staged_strategy: StagedRefinementStrategy, complete_strategy: CompleteRefinementStrategy, dataset: DatasetManager, output_dir: str): ...
    def run(self) -> ExperimentResults: ...
    def _run_staged(self, programs: list[Program]) -> list[StagedResult]: ...
    def _run_complete(self, programs: list[Program]) -> list[CompleteResult]: ...
    def _compute_comparison_metrics(self, staged_results: list[StagedResult], complete_results: list[CompleteResult]) -> ComparisonMetrics: ...
    def _save_results(self, results: ExperimentResults): ...

class ComparisonMetrics:
    staged_mean_discharge: float
    complete_mean_discharge: float
    staged_mean_iterations: float
    complete_mean_iterations: float
    iteration_reduction_ratio: float
    discharge_improvement_pp: float
    p_value: float
    effect_size: float
```

### 4. StatisticalAnalyzer (`src/statistical_analyzer.py`)

**Dependencies:** scipy

```python
class StatisticalAnalyzer:
    def paired_t_test(self, staged_rates: list[float], complete_rates: list[float]) -> TTestResult: ...
    def compute_effect_size(self, staged_rates: list[float], complete_rates: list[float]) -> float: ...
    def analyze_stage_improvements(self, staged_results: list[StagedResult]) -> StageAnalysis: ...
    def analyze_backtracking(self, staged_results: list[StagedResult]) -> BacktrackingAnalysis: ...

class TTestResult:
    p_value: float
    statistic: float
    significant: bool

class StageAnalysis:
    types_contribution: float
    pre_contribution: float
    post_contribution: float
    inv_contribution: float
    most_valuable_stage: StageType

class BacktrackingAnalysis:
    total_events: int
    mean_per_program: float
    programs_with_backtracking: int
```

### 5. ComparisonVisualizer (`src/comparison_visualizer.py`)

**Dependencies:** matplotlib, seaborn

```python
class ComparisonVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics(self, metrics: ComparisonMetrics, target_discharge: float = 50.0, target_iteration_ratio: float = 0.7): ...
    def plot_convergence_comparison(self, staged_results: list[StagedResult], complete_results: list[CompleteResult]): ...
    def plot_per_stage_improvement(self, stage_analysis: StageAnalysis): ...
    def plot_iteration_distribution(self, staged_iterations: list[int], complete_iterations: list[int]): ...
    def plot_backtracking_analysis(self, backtracking_analysis: BacktrackingAnalysis): ...
    def plot_statistical_test(self, staged_rates: list[float], complete_rates: list[float], p_value: float, effect_size: float): ...
```

### 6. DatasetManager (Inherited from H-E1)

**Dependencies:** git, glob (for ACSL by Example benchmark)

```python
class ACSLBenchmarkManager:
    def __init__(self, repo_url: str = "https://github.com/fraunhoferfokus/acsl-by-example.git", num_programs: int = 30): ...
    def clone_benchmark(self, target_dir: str): ...
    def select_programs(self, selection_criteria: dict) -> list[Program]: ...
    def strip_annotations(self, annotated_c: str) -> str: ...
    def extract_gold_spec(self, annotated_c: str) -> str: ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| SpecificationGenerator | `from h_e1.src.llm_client import SpecificationGenerator` | `h-e1/code/src/llm_client.py` |
| FramaCVerifier | `from h_e1.src.verifier import FramaCVerifier, VerificationResult` | `h-e1/code/src/verifier.py` |
| FeedbackExtractor | `from h_e1.src.feedback_parser import FeedbackExtractor, StructuredFeedback` | `h-e1/code/src/feedback_parser.py` |
| ACSLSpec | `from h_e1.src.llm_client import ACSLSpec` | `h-e1/code/src/llm_client.py` |

**Verified from**: docs/youra_research/h-e1/code/ (actual implementation)

**Note:** H-E1 implements the Complete strategy baseline. H-M2 reuses LLM client, verifier, and feedback parser unchanged.

---

## Data Flow

### Experiment-Level Flow

```
ACSLBenchmarkManager → ComparisonExperiment
                       ↓
        [Fork: Staged + Complete paths]
                       ↓
    StagedRefinementStrategy         CompleteRefinementStrategy
             ↓                                  ↓
    Stage 1: Types                    All components (initial)
    Stage 2: Preconditions            ↓
    Stage 3: Postconditions           Iterative refinement
    Stage 4: Invariants               ↓
             ↓                         [Verify + refine loop]
    [Per-stage verification]          ↓
             ↓                         CompleteResult
    StagedResult
                       ↓
        [Collect results from both]
                       ↓
        StatisticalAnalyzer → ComparisonMetrics
                       ↓
        ComparisonVisualizer → Figures
                       ↓
        ExperimentResults
```

### Staged Strategy Iteration Flow

**Stage 1 (Types):**
1. C code → StagedStrategy.refine_stage(stage=TYPES)
2. LLM generates type annotations only
3. Verify partial spec (types only)
4. Iterate up to 3 times or convergence
5. Store StageResult (discharge rate, iterations)

**Stage 2 (Preconditions):**
1. C code + types → StagedStrategy.refine_stage(stage=PRECONDITIONS)
2. LLM generates preconditions given types
3. Verify partial spec (types + pre)
4. Detect backtracking if discharge_rate < previous stage
5. Store StageResult

**Stage 3 (Postconditions):**
1. C code + types + pre → StagedStrategy.refine_stage(stage=POSTCONDITIONS)
2. LLM generates postconditions
3. Verify partial spec (types + pre + post)
4. Store StageResult

**Stage 4 (Invariants):**
1. C code + types + pre + post → StagedStrategy.refine_stage(stage=INVARIANTS)
2. LLM generates loop invariants
3. Verify complete spec
4. Store StageResult

**Final:** Aggregate total_iterations, backtracking_events → StagedResult

### Complete Strategy Iteration Flow

**Iteration 0 (Initial):**
1. C code → CompleteStrategy.generate_complete_spec()
2. LLM generates all components simultaneously (types + pre + post + inv)
3. Verify complete spec → VerificationResult
4. If all_proved: exit
5. Else: extract feedback

**Iteration N (Refinement):**
1. Feedback + current_spec → LLM refinement
2. Refine all components jointly
3. Verify → VerificationResult
4. Check convergence (2 consecutive iterations same discharge rate)
5. If converged or max_iter: exit
6. Else: loop

---

## File Organization

```
h-m2/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── staged_strategy.py        # StagedRefinementStrategy
│   │   ├── complete_strategy.py      # CompleteRefinementStrategy
│   │   ├── comparison_experiment.py  # ComparisonExperiment
│   │   ├── statistical_analyzer.py   # StatisticalAnalyzer
│   │   ├── comparison_visualizer.py  # ComparisonVisualizer
│   │   ├── dataset_manager.py        # ACSLBenchmarkManager
│   │   └── main.py                   # Entry point
│   ├── config/
│   │   └── experiment_config.yaml    # Hyperparameters
│   ├── prompts/
│   │   ├── staged_type_prompt.txt
│   │   ├── staged_pre_prompt.txt
│   │   ├── staged_post_prompt.txt
│   │   ├── staged_inv_prompt.txt
│   │   └── complete_prompt.txt
│   ├── requirements.txt
│   └── run_experiment.py
├── data/
│   ├── acsl-by-example/             # Cloned benchmark (30-50 programs)
│   ├── selected_programs/           # Filtered subset
│   │   ├── program_001.c
│   │   └── ...
│   └── gold_annotations/            # Reference specs (not used during synthesis)
├── results/
│   ├── staged/
│   │   ├── program_001/
│   │   │   ├── stage_types.json
│   │   │   ├── stage_pre.json
│   │   │   ├── stage_post.json
│   │   │   ├── stage_inv.json
│   │   │   └── final_result.json
│   │   └── ...
│   ├── complete/
│   │   ├── program_001/
│   │   │   ├── iteration_0.json
│   │   │   ├── iteration_1.json
│   │   │   └── final_result.json
│   │   └── ...
│   ├── comparison_metrics.json
│   ├── statistical_analysis.json
│   └── experiment_log.md
├── figures/
│   ├── gate_metrics_comparison.png
│   ├── convergence_comparison.png
│   ├── per_stage_improvement.png
│   ├── iteration_distribution.png
│   ├── backtracking_analysis.png
│   └── statistical_test.png
└── 04_validation.md
```

---

## Configuration Management

### Experiment Config (`config/experiment_config.yaml`)

```yaml
# Inherited from H-E1 (reused for both strategies)
llm:
  model: "claude-opus-4-5"
  api_key_env: "ANTHROPIC_API_KEY"
  temperature:
    generation: 0.7
    refinement: 0.5
  max_tokens: 4096
  timeout_seconds: 60

verifier:
  frama_c_path: "frama-c"
  timeout_per_vc: 10
  solvers: ["alt-ergo", "z3"]
  wp_model: "Typed"

# Strategy-specific parameters
staged_strategy:
  max_iterations_per_stage: 3
  stages: ["types", "preconditions", "postconditions", "invariants"]
  enable_backtracking_detection: true

complete_strategy:
  max_iterations: 10
  convergence_criterion: "2_consecutive_same"

# Dataset
dataset:
  benchmark_repo: "https://github.com/fraunhoferfokus/acsl-by-example.git"
  num_programs: 30
  selection_criteria:
    min_lines: 10
    max_lines: 200
    exclude_features: ["floating_point", "concurrency"]
  seed: 42

# Experiment
experiment:
  strategies: ["staged", "complete"]
  statistical_test: "paired_t_test"
  significance_threshold: 0.05

# Paths
paths:
  data_dir: "data"
  results_dir: "results"
  figures_dir: "figures"

# Gate Criteria
gate:
  target_iteration_ratio: 0.7  # Staged ≤ 70% Complete iterations
  target_discharge_improvement_pp: 5.0  # Staged ≥ Complete + 5pp
  require_statistical_significance: true
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset Acquisition | Clone ACSL by Example, select 30-50 programs, strip annotations | 8 | git clone(2) + selection(2) + annotation stripping(2) + validation(2) |
| A-2 | Staged Strategy | Implement StagedRefinementStrategy with 4-stage sequential refinement | 16 | stage logic(5) + partial verification(4) + prompt templates(4) + backtracking detection(3) |
| A-3 | Complete Strategy | Adapt H-E1 RefinementLoop to CompleteRefinementStrategy interface | 10 | adapter wrapper(4) + convergence logic(3) + result mapping(3) |
| A-4 | Comparison Orchestrator | Implement ComparisonExperiment to run both strategies on same programs | 12 | orchestration(4) + parallel execution(3) + result aggregation(3) + checkpointing(2) |
| A-5 | Statistical Analysis | Implement paired t-test, effect size, stage analysis, backtracking analysis | 14 | paired t-test(4) + effect size(3) + stage analysis(4) + backtracking(3) |
| A-6 | Visualization | Create 6 comparison plots (gate metrics, convergence, stages, distribution, backtracking, statistical) | 11 | gate plot(2) + convergence(2) + stages(2) + distribution(2) + backtracking(2) + statistical(1) |
| A-7 | Experiment Runner | End-to-end pipeline with error recovery, progress tracking, validation report generation | 13 | pipeline(5) + error handling(3) + progress tracking(2) + report generation(3) |

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): [A-2, A-5]
- Medium (9-13): [A-3, A-4, A-6, A-7]
- Low (4-8): [A-1]

**Total Complexity:** 84 points (7 tasks)

---

## Critical Design Decisions

### 1. Reuse H-E1 Infrastructure (LLM + Verifier + Feedback)

**Decision:** Import H-E1 modules directly instead of reimplementing.

**Rationale:**
- Controlled experiment requires identical LLM client and verifier setup
- H-E1 validated these components (62.9% discharge rate)
- Only refinement strategy changes (Staged vs Complete)

**Trade-off:** Dependency on H-E1 codebase, but eliminates confounding variables.

### 2. Per-Stage Budget (3 iterations each) vs Total Budget (12 iterations)

**Decision:** Limit each stage to 3 iterations (total 12 max) vs Complete strategy's 10 iterations.

**Rationale:**
- Fair comparison: similar total iteration budget
- Prevents one stage from consuming all iterations
- Staged gets slight budget increase (12 vs 10) to account for stage overhead

**Alternative considered:** Equal total budget (10 iterations distributed across stages) - rejected because uneven stage complexity.

### 3. Partial Verification After Each Stage

**Decision:** Run Frama-C after each stage completion (4 times per program) vs only final verification.

**Rationale:**
- Detects backtracking early (later stage invalidates earlier spec)
- Enables per-stage improvement tracking (key metric)
- Mirrors real-world incremental development

**Trade-off:** 4× verifier invocations, but necessary to test hypothesis.

### 4. Backtracking Detection via Discharge Rate Decrease

**Decision:** Count backtracking event when discharge_rate[stage_N] < discharge_rate[stage_N-1].

**Rationale:**
- Simple heuristic aligned with hypothesis test
- Quantifies cost of staged approach
- No complex dependency graph analysis needed (PoC scope)

**Limitation:** May miss subtle backtracking (e.g., same discharge rate but different VCs failed).

---

## Validation Strategy

### Unit Tests

**Test Coverage:**
- StagedRefinementStrategy: Mock stage progression with synthetic specs
- CompleteRefinementStrategy: Verify convergence detection logic
- StatisticalAnalyzer: Test with known distributions (validate p-value)
- ComparisonExperiment: Test orchestration with 2 mock programs

### Integration Tests

**End-to-End Test:**
1. Single program (simple binary search)
2. Run both strategies
3. Verify: Staged produces 4 stage results, Complete produces iteration history
4. Verify: Comparison metrics computed correctly
5. Verify: All 6 plots generated

### Validation Criteria (Phase 4)

**Code Validation:**
- All tests pass
- H-E1 modules import successfully
- No hardcoded API keys or paths

**Experiment Validation:**
- Both strategies complete on 30-50 programs
- Statistical analysis produces p-value and effect size
- All 6 visualization figures generated
- Gate decision (PASS/FAIL/NEUTRAL) in 04_validation.md

---

**Architecture Version:** 1.0  
**Status:** Ready for Phase 4 Implementation  
**Next Step:** Phase 4 Coder implements modules following this specification
