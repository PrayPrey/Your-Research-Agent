# System Architecture: H-M1 Information Gradient Validation

**Date:** 2026-07-11  
**Hypothesis:** H-M1 - Proof discharge rate scales monotonically with feedback richness  
**PRD:** 03_prd.md  
**Experiment Brief:** 02c_experiment_brief.md  
**Architecture Type:** MECHANISM - Ablation study with 4 feedback conditions

---

## Knowledge Base Application

Applied: Ablation experiment patterns (controlled comparison, shared test set)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from base code (h-e1)  
**Analyzed Path:** `/workspace/TEST_verifai/docs/youra_research/h-e1/code/`  
**Findings:** Existing refinement loop architecture verified. Module structure: src/*.py with relative imports.

---

## System Context

### Core Hypothesis Test

**Question:** Does proof discharge rate scale monotonically with feedback information content?

**Mechanism:** Information Gradient - Testing causal relationship between feedback richness and performance across 4 controlled conditions.

**Success Criteria:**
1. Monotonic ordering: FullStructured > ObligationSlice > TagOnly > RawError
2. Adjacent gaps ≥10 percentage points
3. Regression: β > 0, p < 0.05

### System Boundaries

**Input:** 30-50 C programs (ACSL-by-Example benchmark)  
**Output:** Per-condition discharge rates + statistical analysis + gate decision  
**External Dependencies:**
- Base h-e1 code (refinement loop, verifier wrapper, LLM client)
- Anthropic API (Claude Opus 4.5)
- Frama-C 32.0 + WP + solvers

**Out of Scope:**
- Multi-model comparison (use single LLM)
- Adaptive feedback selection (4 fixed conditions)
- Human-in-the-loop refinement

---

## Module Structure

### 1. FeedbackAblator (`src/feedback_ablator.py`)

**Dependencies:** feedback_parser (from h-e1)

```python
class FeedbackAblator:
    def __init__(self, condition: str): ...
    def ablate_feedback(self, full_feedback: StructuredFeedback) -> dict: ...
    def get_condition_name(self) -> str: ...

class FeedbackCondition:
    FULL_STRUCTURED = "FullStructured"
    OBLIGATION_SLICE = "ObligationSlice"
    TAG_ONLY = "TagOnly"
    RAW_ERROR = "RawError"
```

### 2. AblationExperiment (`src/ablation_experiment.py`)

**Dependencies:** refinement_loop, feedback_ablator, dataset, metrics

```python
class AblationExperiment:
    def __init__(self, config: dict, base_refinement_loop: IterativeRefinementLoop): ...
    def run_condition(self, condition: str, programs: list) -> ConditionResults: ...
    def run_full_ablation(self, programs: list) -> AblationResults: ...
    def _run_single_trial(self, program: Program, condition: str) -> TrialResult: ...

class ConditionResults:
    condition: str
    discharge_rates: list[float]
    mean_rate: float
    std_rate: float
    iterations: list[int]
    compute_budget: dict

class AblationResults:
    results_by_condition: dict[str, ConditionResults]
    raw_trials: list[TrialResult]
```

### 3. StatisticalAnalyzer (`src/statistical_analyzer.py`)

**Dependencies:** scipy, numpy

```python
class StatisticalAnalyzer:
    def __init__(self, significance_level: float = 0.05): ...
    def test_monotonic_ordering(self, condition_means: dict) -> MonotonicTest: ...
    def test_adjacent_gaps(self, condition_means: dict, threshold: float = 10.0) -> GapTest: ...
    def run_regression(self, ablation_results: AblationResults) -> RegressionResult: ...
    def check_compute_fairness(self, ablation_results: AblationResults) -> FairnessResult: ...
    def make_gate_decision(self, all_tests: dict) -> GateDecision: ...

class MonotonicTest:
    passed: bool
    ordering: list[str]
    violations: list[str]

class GapTest:
    passed: bool
    gaps: dict[str, float]
    failed_gaps: list[str]

class RegressionResult:
    coefficient: float
    p_value: float
    r_squared: float
    significant: bool

class GateDecision:
    status: str  # SATISFIED | FAILED
    passing_tests: list[str]
    failing_tests: list[str]
    reason: str
```

### 4. AblationVisualizer (`src/ablation_visualizer.py`)

**Dependencies:** matplotlib, seaborn, visualizer (from h-e1)

```python
class AblationVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_monotonic_ordering(self, condition_results: dict, output_path: str): ...
    def plot_per_program_heatmap(self, raw_trials: list, output_path: str): ...
    def plot_regression(self, regression_data: list, result: RegressionResult, output_path: str): ...
    def plot_compute_budget_analysis(self, raw_trials: list, output_path: str): ...
    def generate_all_figures(self, ablation_results: AblationResults, stats: dict): ...
```

### 5. ResultsDocumentor (`src/results_documentor.py`)

**Dependencies:** yaml

```python
class ResultsDocumentor:
    def __init__(self, hypothesis_folder: str): ...
    def generate_validation_report(self, ablation_results: AblationResults, stats: dict, gate_decision: GateDecision) -> str: ...
    def update_verification_state(self, gate_decision: GateDecision, stats: dict): ...
    def save_validation_report(self, report_content: str, output_path: str): ...
```

### 6. AblationRunner (`src/main_ablation.py`)

**Dependencies:** All modules

```python
class AblationRunner:
    def __init__(self, config_path: str): ...
    def run(self): ...
    def _setup_components(self): ...
    def _load_benchmark(self) -> list[Program]: ...
    def _run_ablation_study(self, programs: list) -> AblationResults: ...
    def _analyze_results(self, results: AblationResults) -> dict: ...
    def _generate_outputs(self, results: AblationResults, stats: dict): ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| SpecificationGenerator | `from h_e1.src.llm_client import SpecificationGenerator` | `h-e1/code/src/llm_client.py` |
| FramaCVerifier | `from h_e1.src.verifier import FramaCVerifier` | `h-e1/code/src/verifier.py` |
| FeedbackExtractor | `from h_e1.src.feedback_parser import FeedbackExtractor` | `h-e1/code/src/feedback_parser.py` |
| IterativeRefinementLoop | `from h_e1.src.refinement_loop import IterativeRefinementLoop` | `h-e1/code/src/refinement_loop.py` |
| DatasetManager | `from h_e1.src.dataset import DatasetManager` | `h-e1/code/src/dataset.py` |
| MetricsTracker | `from h_e1.src.metrics import MetricsTracker` | `h-e1/code/src/metrics.py` |
| StructuredFeedback | `from h_e1.src.feedback_parser import StructuredFeedback` | `h-e1/code/src/feedback_parser.py` |

**Verified from:** `/workspace/TEST_verifai/docs/youra_research/h-e1/code/` (actual implementation)

---

## Data Flow

### End-to-End Pipeline

```
DatasetManager → AblationRunner → AblationExperiment
                                   ↓
                  [For each condition × program]
                                   ↓
                  FeedbackAblator → IterativeRefinementLoop (h-e1)
                                   ↓
                  ConditionResults → StatisticalAnalyzer
                                   ↓
                  GateDecision → ResultsDocumentor + AblationVisualizer
```

### Ablation Flow (Per Condition)

**Step 1: Condition Setup**
1. Load programs from DatasetManager
2. Initialize FeedbackAblator with condition type
3. Create modified refinement loop with ablated feedback

**Step 2: Trial Execution**
1. For program P, condition C:
   - Run IterativeRefinementLoop (reuse from h-e1)
   - Apply FeedbackAblator to filter feedback dimensions
   - Record discharge rate, iterations, compute budget
2. Store TrialResult(program_id, condition, metrics)

**Step 3: Statistical Analysis**
1. Aggregate ConditionResults per condition
2. Test monotonic ordering (mean comparison)
3. Test adjacent gaps (≥10pp threshold)
4. Run regression (ordinal feedback → discharge rate)
5. Check compute budget fairness (no condition uses >20% more)

**Step 4: Gate Decision**
1. Combine all test results
2. Make gate decision: SATISFIED (all pass) | FAILED (any fail)
3. Generate validation report + figures

---

## File Organization

```
h-m1/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── feedback_ablator.py       # NEW - Ablation controller
│   │   ├── ablation_experiment.py    # NEW - Experiment orchestrator
│   │   ├── statistical_analyzer.py   # NEW - Hypothesis testing
│   │   ├── ablation_visualizer.py    # NEW - 4 ablation plots
│   │   ├── results_documentor.py     # NEW - Report + state update
│   │   └── main_ablation.py          # NEW - Entry point
│   ├── config/
│   │   └── ablation_config.yaml      # Extends h-e1 config
│   ├── requirements.txt              # scipy + h-e1 dependencies
│   └── run_ablation.py               # Entry point
├── results/
│   ├── trials/                       # Per-trial results
│   │   ├── program_001_FullStructured.json
│   │   ├── program_001_ObligationSlice.json
│   │   ├── program_001_TagOnly.json
│   │   ├── program_001_RawError.json
│   │   └── ...
│   ├── condition_aggregates.json     # Mean/std per condition
│   ├── statistical_tests.json        # Test results
│   └── experiment_log.md             # Human-readable log
├── figures/
│   ├── gate_metrics_comparison.png   # Required gate plot
│   ├── monotonic_ordering.png        # Line plot with CIs
│   ├── per_program_heatmap.png       # Programs × Conditions
│   ├── regression_plot.png           # Feedback richness vs rate
│   └── compute_budget_analysis.png   # Fairness check
└── 04_validation.md                  # Results report (Phase 4 output)
```

---

## Configuration Management

### Ablation Config (`config/ablation_config.yaml`)

```yaml
# Inherit from h-e1 base config
base_config: "../h-e1/code/config/experiment_config.yaml"

# Ablation-specific
ablation:
  conditions:
    - "FullStructured"
    - "ObligationSlice"
    - "TagOnly"
    - "RawError"
  control_variables:
    same_llm_model: true
    same_random_seed: 42
    same_compute_budget: true
    same_verifier_config: true

# Dataset (larger than h-e1)
dataset:
  name: "acsl-by-example"
  num_programs: 30  # Minimum for statistical power
  selection_criteria:
    program_size_lines: [10, 100]
    proof_obligations_count: [5, 20]
    algorithm_diversity: true

# Statistical Analysis
statistics:
  significance_level: 0.05
  monotonic_test: true
  gap_threshold_pp: 10.0  # Adjacent gaps ≥10 percentage points
  regression_type: "linear_monotonic"
  compute_fairness_threshold: 0.20  # Max 20% compute delta

# Gate Criteria
gate:
  require_monotonic_ordering: true
  require_adjacent_gaps: true
  require_significant_regression: true
  gate_type: "MUST_WORK"
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Feedback Ablator | Implement 4-condition feedback filtering logic | 9 | condition logic(3) + filtering(3) + integration(2) + testing(1) |
| M-2 | Ablation Experiment | Orchestrate program × condition trials with h-e1 loop | 12 | trial runner(4) + condition iteration(3) + checkpointing(3) + result aggregation(2) |
| M-3 | Statistical Analysis | Implement 3 hypothesis tests + compute fairness check | 16 | monotonic test(4) + gap test(3) + regression(5) + fairness(2) + gate logic(2) |
| M-4 | Ablation Visualizer | Generate 4 ablation-specific plots | 11 | ordering plot(3) + heatmap(3) + regression plot(3) + budget plot(2) |
| M-5 | Results Documentor | Auto-generate 04_validation.md + update verification_state | 8 | report template(3) + state update(2) + figure integration(2) + markdown(1) |
| M-6 | Dataset Expansion | Select 30-50 programs from ACSL-by-Example (vs 10 in h-e1) | 7 | repository clone(1) + selection script(3) + validation(2) + preprocessing(1) |
| M-7 | Integration Runner | End-to-end ablation orchestration with error recovery | 13 | orchestration(4) + error handling(3) + logging(2) + checkpoint recovery(2) + results pipeline(2) |

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): [M-3]
- Medium (9-13): [M-1, M-2, M-4, M-7]
- Low (4-8): [M-5, M-6]

**Total Complexity:** 76 points (7 tasks)

---

## Critical Design Decisions

### 1. Reuse h-e1 Refinement Loop (No Reimplementation)

**Decision:** Import IterativeRefinementLoop from h-e1, apply FeedbackAblator as wrapper.

**Rationale:**
- Ablation requires identical refinement logic across conditions
- Only variable is feedback content, not loop structure
- Avoid code duplication and divergence

**Implementation:** 
```python
# h-m1/src/ablation_experiment.py
from h_e1.src.refinement_loop import IterativeRefinementLoop

ablated_feedback = self.ablator.ablate_feedback(full_feedback)
result = self.refinement_loop.synthesize(program, ablated_feedback)
```

### 2. Ordinal Encoding for Regression

**Decision:** Encode feedback conditions as ordinal variable (1=Raw, 2=Tag, 3=Obl, 4=Full).

**Rationale:**
- Information content has natural ordering
- Linear regression with monotonic constraint tests gradient hypothesis
- Interpretable coefficient (pp increase per richness level)

### 3. Checkpoint at Trial Level (Not Iteration Level)

**Decision:** Save results after each program × condition trial, not per refinement iteration.

**Rationale:**
- Iteration-level checkpointing handled by h-e1 refinement loop
- Ablation checkpointing needs trial-level granularity for resume
- Smaller checkpoint files, faster recovery

---

## Validation Strategy

### Unit Tests

**Test Coverage:**
- FeedbackAblator: Test 4 condition filters with synthetic StructuredFeedback
- StatisticalAnalyzer: Test monotonic/gap/regression logic with mock data
- AblationExperiment: Test single trial execution with mock loop

### Integration Tests

**End-to-End Test:**
1. 4 programs × 4 conditions = 16 trials
2. Expected: All trials complete, results aggregated correctly
3. Verify: Statistical tests run, gate decision made, plots generated

### Validation Criteria (Phase 4)

**Code Validation:**
- All tests pass
- Imports from h-e1 resolve correctly
- No hardcoded paths/keys

**Experiment Validation:**
- Monotonic ordering test produces valid result (pass/fail)
- All 4 plots generated successfully
- 04_validation.md contains gate decision

---

**Architecture Version:** 1.0  
**Status:** Ready for Phase 4 Implementation  
**Next Step:** Phase 4 Coder implements modules following this specification
