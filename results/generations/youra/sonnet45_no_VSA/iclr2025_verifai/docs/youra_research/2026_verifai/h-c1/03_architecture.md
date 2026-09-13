# System Architecture: H-C1 Compute-Matched Control Experiment

**Date:** 2026-07-11  
**Hypothesis:** H-C1 - Iterative feedback outperforms self-consistency sampling under compute-matched budgets by ≥10pp  
**PRD:** 03_prd.md  
**Experiment Brief:** 02c_experiment_brief.md  
**Architecture Type:** CONTROL - Compute-matched baseline comparison

---

## Knowledge Base Application

Applied: Modular pipeline patterns, compute tracking patterns

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns found from base code (h-m1)  
**Analyzed Path:** `docs/youra_research/h-m1/code/`  
**Findings:** Reusing LLM client, verifier wrapper, refinement loop, dataset manager. Module structure: src/*.py with relative imports.

---

## System Context

### Core Hypothesis Test

**Question:** Does iterative feedback with structured verifier feedback outperform self-consistency sampling when given equal compute budgets (tokens + verifier time)?

**Mechanism:** Compute-matched control - Testing whether performance gains are from feedback content vs. simply more compute budget.

**Success Criteria:**
1. IterativeFeedback discharge rate ≥ SelfConsistency discharge rate + 10pp
2. Statistical significance: p < 0.05 (paired t-test)
3. Effect size: Cohen's d ≥ 0.5
4. Compute fairness: Token and time ratios within 0.90-1.10

### System Boundaries

**Input:** 50 C programs (ACSL-by-Example benchmark, from h-m1)  
**Output:** Per-baseline discharge rates + compute budgets + statistical analysis + gate decision  
**External Dependencies:**
- Base h-m1 code (refinement loop, verifier wrapper, LLM client, dataset, metrics)
- Anthropic API (Claude Opus 4.5, matching h-m1)
- Frama-C 32.0 + WP + solvers

**Out of Scope:**
- Multi-model comparison (use single LLM from h-m1)
- Temperature sweep (fixed: 0.7 sampling, 0.2 refinement)
- Adaptive N per program (use global N from validation set)
- Human-in-the-loop baseline

---

## Module Structure

### 1. ComputeBudgetTracker (`src/core/compute_budget.py`)

**Dependencies:** None

```python
@dataclass
class ComputeBudget:
    total_tokens: int
    verifier_time_seconds: float
    llm_api_calls: int
    iterations: int

class ComputeBudgetTracker:
    def __init__(self, target_budget: Optional[ComputeBudget] = None): ...
    def record_llm_call(self, prompt_tokens: int, completion_tokens: int): ...
    def record_verifier_call(self, execution_time: float): ...
    def start_iteration(self): ...
    def get_budget(self) -> ComputeBudget: ...
    def exceeds_target(self, tolerance: float = 0.10) -> bool: ...
    def fork(self) -> ComputeBudgetTracker: ...
```

### 2. IterativeFeedbackBaseline (`src/baselines/iterative_feedback.py`)

**Dependencies:** h-m1 refinement_loop, feedback_parser, compute_budget

```python
class IterativeFeedbackBaseline:
    def __init__(
        self, 
        refinement_loop: IterativeRefinementLoop,  # From h-m1
        max_iterations: int = 10,
        temperature: float = 0.2
    ): ...
    def run(self, program: Program, budget_tracker: ComputeBudgetTracker) -> BaselineResult: ...
    def _check_convergence(self, current_spec: str, previous_spec: str, iteration: int) -> bool: ...

@dataclass
class BaselineResult:
    program_id: str
    final_spec: str
    discharge_rate: float
    compute_budget: ComputeBudget
    iterations_or_samples: int
    trajectory: List[IterationSnapshot]
```

### 3. SelfConsistencyBaseline (`src/baselines/self_consistency.py`)

**Dependencies:** h-m1 llm_client, verifier, compute_budget

```python
class SelfConsistencyBaseline:
    def __init__(
        self,
        llm_client: SpecificationGenerator,  # From h-m1
        verifier: FramaCVerifier,  # From h-m1
        selection_strategy: str = "best_of_n",
        temperature: float = 0.7
    ): ...
    def run(self, program: Program, N: int, budget_tracker: ComputeBudgetTracker) -> BaselineResult: ...
    def _generate_samples(self, program: Program, N: int, budget_tracker: ComputeBudgetTracker) -> List[ACSLSpec]: ...
    def _select_best_of_n(self, samples: List[ACSLSpec], results: List[VerificationResult]) -> int: ...
    def _select_by_voting(self, samples: List[ACSLSpec], results: List[VerificationResult]) -> ACSLSpec: ...
```

### 4. HybridBaseline (`src/baselines/hybrid.py`)

**Dependencies:** h-m1 refinement_loop, llm_client, verifier, compute_budget

```python
class HybridBaseline:
    def __init__(
        self,
        llm_client: SpecificationGenerator,
        verifier: FramaCVerifier,
        refinement_loop: IterativeRefinementLoop,
        initial_samples: int = 3
    ): ...
    def run(self, program: Program, budget_tracker: ComputeBudgetTracker) -> BaselineResult: ...
    def _sample_phase(self, program: Program, K: int, budget_tracker: ComputeBudgetTracker) -> ACSLSpec: ...
    def _refinement_phase(self, program: Program, initial_spec: ACSLSpec, budget_tracker: ComputeBudgetTracker) -> BaselineResult: ...
    def _estimate_affordable_iterations(self, remaining_budget: ComputeBudget) -> int: ...
```

### 5. ExperimentRunner (`src/core/experiment_runner.py`)

**Dependencies:** baselines, compute_budget, h-m1 dataset

```python
class ExperimentRunner:
    def __init__(
        self,
        baseline1: IterativeFeedbackBaseline,
        baseline2: SelfConsistencyBaseline,
        baseline3: HybridBaseline,
        dataset_manager: DatasetManager  # From h-m1
    ): ...
    def calibrate_budgets(self, validation_programs: List[Program]) -> Tuple[ComputeBudget, int]: ...
    def run_test_set_evaluation(
        self, 
        test_programs: List[Program], 
        avg_budget: ComputeBudget, 
        N: int
    ) -> ExperimentResults: ...
    def _run_single_program(self, program: Program, avg_budget: ComputeBudget, N: int) -> ProgramResult: ...
    def _save_checkpoint(self, results: List[ProgramResult], checkpoint_path: str): ...

@dataclass
class ExperimentResults:
    program_results: List[ProgramResult]
    calibration_budget: ComputeBudget
    N_samples: int
    
@dataclass
class ProgramResult:
    program_id: str
    baseline1_result: BaselineResult
    baseline2_result: BaselineResult
    baseline3_result: BaselineResult
```

### 6. StatisticalAnalyzer (`src/analysis/statistical_tests.py`)

**Dependencies:** scipy, numpy

```python
class StatisticalAnalyzer:
    def __init__(self, significance_level: float = 0.05): ...
    def primary_hypothesis_test(self, results: ExperimentResults) -> HypothesisTestResult: ...
    def validate_compute_fairness(self, results: ExperimentResults) -> ComputeFairnessResult: ...
    def per_program_analysis(self, results: ExperimentResults) -> PerProgramStats: ...
    def make_gate_decision(
        self, 
        hypothesis_test: HypothesisTestResult, 
        fairness: ComputeFairnessResult,
        per_program: PerProgramStats
    ) -> GateDecision: ...

@dataclass
class HypothesisTestResult:
    mean_baseline1: float
    mean_baseline2: float
    mean_difference: float
    t_statistic: float
    p_value: float
    cohens_d: float
    gate_satisfied: bool

@dataclass
class ComputeFairnessResult:
    baseline1_avg_tokens: float
    baseline2_avg_tokens: float
    token_ratio: float
    token_budget_fair: bool
    baseline1_avg_time: float
    baseline2_avg_time: float
    time_ratio: float
    time_budget_fair: bool
    overall_fair: bool

@dataclass
class GateDecision:
    status: str  # SATISFIED | FAILED
    criteria: Dict[str, bool]
    failure_reasons: List[str]
```

### 7. Visualizer (`src/analysis/visualizer.py`)

**Dependencies:** matplotlib, seaborn

```python
class ComputeMatchedVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_primary_comparison(self, results: ExperimentResults, output_path: str): ...
    def plot_per_program_heatmap(self, results: ExperimentResults, output_path: str): ...
    def plot_compute_budget_scatter(self, results: ExperimentResults, output_path: str): ...
    def plot_gap_distribution(self, results: ExperimentResults, output_path: str): ...
    def plot_hybrid_analysis(self, results: ExperimentResults, output_path: str): ...
    def generate_all_figures(self, results: ExperimentResults, stats: Dict): ...
```

### 8. ReportGenerator (`src/analysis/report_generator.py`)

**Dependencies:** yaml

```python
class ReportGenerator:
    def __init__(self, hypothesis_folder: str): ...
    def generate_validation_report(
        self, 
        results: ExperimentResults, 
        stats: Dict, 
        gate_decision: GateDecision
    ) -> str: ...
    def update_verification_state(self, gate_decision: GateDecision, stats: Dict): ...
    def save_validation_report(self, report_content: str, output_path: str): ...
    def export_results_json(self, results: ExperimentResults, output_path: str): ...
```

### 9. CheckpointManager (`src/core/checkpoint_manager.py`)

**Dependencies:** json

```python
class CheckpointManager:
    def __init__(self, checkpoint_dir: str): ...
    def save_checkpoint(self, results: List[ProgramResult], metadata: Dict): ...
    def load_checkpoint(self) -> Tuple[List[ProgramResult], Dict]: ...
    def checkpoint_exists(self) -> bool: ...
    def get_completed_program_ids(self) -> Set[str]: ...
```

### 10. MainOrchestrator (`src/main.py`)

**Dependencies:** All modules

```python
class MainOrchestrator:
    def __init__(self, config_path: str): ...
    def run(self): ...
    def _setup_components(self): ...
    def _stage1_calibration(self) -> Tuple[ComputeBudget, int]: ...
    def _stage2_evaluation(self, avg_budget: ComputeBudget, N: int) -> ExperimentResults: ...
    def _stage3_analysis(self, results: ExperimentResults) -> Dict: ...
    def _stage4_reporting(self, results: ExperimentResults, stats: Dict): ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| SpecificationGenerator | `from h_m1.code.code.src.llm_client import SpecificationGenerator` | `h-m1/code/code/src/llm_client.py` |
| FramaCVerifier | `from h_m1.code.code.src.verifier import FramaCVerifier` | `h-m1/code/code/src/verifier.py` |
| FeedbackExtractor | `from h_m1.code.code.src.feedback_parser import FeedbackExtractor` | `h-m1/code/code/src/feedback_parser.py` |
| IterativeRefinementLoop | `from h_m1.code.code.src.refinement_loop import IterativeRefinementLoop` | `h-m1/code/code/src/refinement_loop.py` |
| DatasetManager | `from h_m1.code.code.src.dataset import DatasetManager` | `h-m1/code/code/src/dataset.py` |
| MetricsTracker | `from h_m1.code.code.src.metrics import MetricsTracker` | `h-m1/code/code/src/metrics.py` |
| ACSLSpec | `from h_m1.code.code.src.llm_client import ACSLSpec` | `h-m1/code/code/src/llm_client.py` |
| VerificationResult | `from h_m1.code.code.src.verifier import VerificationResult` | `h-m1/code/code/src/verifier.py` |
| StructuredFeedback | `from h_m1.code.code.src.feedback_parser import StructuredFeedback` | `h-m1/code/code/src/feedback_parser.py` |
| Program | `from h_m1.code.code.src.dataset import Program` | `h-m1/code/code/src/dataset.py` |

**Verified from:** `docs/youra_research/h-m1/code/` (actual implementation)

---

## Data Flow

### Two-Stage Execution Pipeline

```
Stage 1: Calibration (Validation Set - 15 programs)
  DatasetManager → IterativeFeedbackBaseline → ComputeBudgetTracker
                                              ↓
                                  Compute avg_budget, avg_iterations
                                              ↓
                                  Determine N for SelfConsistency

Stage 2: Evaluation (Test Set - 50 programs)
  For each program:
    ↓
    Baseline 1: IterativeFeedbackBaseline → BaselineResult
    Baseline 2: SelfConsistencyBaseline(N) → BaselineResult
    Baseline 3: HybridBaseline → BaselineResult
    ↓
    ExperimentRunner → ProgramResult
    ↓
    [Checkpoint every 10 programs]

Stage 3: Analysis
  ExperimentResults → StatisticalAnalyzer → HypothesisTestResult
                                          → ComputeFairnessResult
                                          → GateDecision

Stage 4: Reporting
  GateDecision → ReportGenerator → 04_validation.md
               → Visualizer → figures/
               → verification_state.yaml update
```

### Baseline 1: Iterative Feedback Flow

```
Program → IterativeRefinementLoop (from h-m1)
           ↓
           [Initial generation]
           LLM (temp=0.2) → ACSLSpec
           ↓
           FramaCVerifier → VerificationResult
           ↓
           [If not converged]
           FeedbackExtractor → StructuredFeedback
           ↓
           LLM (temp=0.2, with feedback) → Refined ACSLSpec
           ↓
           [Repeat max 10 iterations]
           ↓
           Final BaselineResult + ComputeBudget
```

### Baseline 2: Self-Consistency Flow

```
Program → SelfConsistencyBaseline
           ↓
           [Generate N independent samples]
           For i in range(N):
             LLM (temp=0.7, seed=42+i*1000) → ACSLSpec_i
             FramaCVerifier → VerificationResult_i
           ↓
           [Selection]
           Best-of-N: Select sample with max discharge rate
           ↓
           Final BaselineResult + ComputeBudget
```

### Baseline 3: Hybrid Flow

```
Program → HybridBaseline
           ↓
           Phase 1: Sample (K=3)
           For i in range(3):
             LLM (temp=0.7) → ACSLSpec_i
             FramaCVerifier → VerificationResult_i
           Select best_initial_spec
           ↓
           Phase 2: Refine (remaining budget)
           IterativeRefinementLoop(best_initial_spec)
           ↓
           Final BaselineResult + ComputeBudget
```

---

## Storage Schema

### Results Database Structure

```
h-c1/
├── results/
│   ├── calibration/
│   │   ├── program_val_001.json
│   │   ├── program_val_002.json
│   │   └── ...
│   │   └── calibration_summary.json
│   ├── test_set/
│   │   ├── program_001_all_baselines.json
│   │   ├── program_002_all_baselines.json
│   │   └── ...
│   ├── checkpoints/
│   │   ├── checkpoint_10.json
│   │   ├── checkpoint_20.json
│   │   └── ...
│   ├── experiment_results.json
│   └── experiment_log.md
├── figures/
│   ├── primary_comparison.png
│   ├── per_program_heatmap.png
│   ├── compute_budget_scatter.png
│   ├── gap_distribution.png
│   └── hybrid_analysis.png
└── 04_validation.md
```

### JSON Schema Examples

**ProgramResult JSON:**
```json
{
  "program_id": "array_max_001",
  "baseline1": {
    "final_spec": "...",
    "discharge_rate": 80.0,
    "compute_budget": {
      "total_tokens": 11850,
      "verifier_time_seconds": 53.0,
      "llm_api_calls": 3,
      "iterations": 3
    },
    "trajectory": [...]
  },
  "baseline2": {
    "final_spec": "...",
    "discharge_rate": 55.0,
    "compute_budget": {
      "total_tokens": 9900,
      "verifier_time_seconds": 45.0,
      "llm_api_calls": 3,
      "iterations": 3
    }
  },
  "baseline3": {...}
}
```

**CalibrationSummary JSON:**
```json
{
  "validation_programs": 15,
  "avg_budget": {
    "total_tokens": 12000,
    "verifier_time_seconds": 55.0,
    "iterations": 7
  },
  "N_samples_computed": 3,
  "single_shot_estimates": {
    "avg_tokens": 3300,
    "avg_verifier_time": 15.0
  }
}
```

---

## File Organization

```
h-c1/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── baselines/
│   │   │   ├── __init__.py
│   │   │   ├── iterative_feedback.py    # Reuses h-m1 refinement loop
│   │   │   ├── self_consistency.py      # NEW - N-sample generation
│   │   │   └── hybrid.py                # NEW - Sample + refine
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── compute_budget.py        # NEW - Budget tracking
│   │   │   ├── experiment_runner.py     # NEW - Orchestration
│   │   │   └── checkpoint_manager.py    # NEW - Checkpointing
│   │   ├── analysis/
│   │   │   ├── __init__.py
│   │   │   ├── statistical_tests.py     # NEW - Hypothesis testing
│   │   │   ├── visualizer.py            # NEW - 5 plots
│   │   │   └── report_generator.py      # NEW - Report + state update
│   │   └── main.py                      # NEW - Entry point
│   ├── config/
│   │   └── h-c1-experiment.yaml         # Configuration
│   ├── requirements.txt
│   └── run_experiment.py                # CLI entry point
├── results/                             # Generated during execution
├── figures/                             # Generated during execution
└── 04_validation.md                     # Generated by ReportGenerator
```

---

## Configuration Management

### Experiment Config (`config/h-c1-experiment.yaml`)

```yaml
experiment:
  hypothesis_id: h-c1
  dataset: h-m1-benchmark
  validation_set_size: 15
  test_set_size: 50

llm:
  model: claude-opus-4-5
  temperature_refinement: 0.2
  temperature_sampling: 0.7
  max_tokens: 4096
  top_p: 0.95

verifier:
  tool: frama-c
  version: 32.0
  timeout_per_obligation: 10
  provers: [alt-ergo-2.6.2, z3-4.15.2, cvc5-1.3.3]

baselines:
  iterative_feedback:
    max_iterations: 10
    convergence_check: 2_iterations_no_change
    temperature: 0.2
  self_consistency:
    compute_matched: true
    selection_strategy: best_of_n
    min_samples: 3
    temperature: 0.7
  hybrid:
    initial_samples: 3
    budget_allocation: [0.3, 0.7]  # sampling, refinement

compute_budget:
  fairness_tolerance: 0.10
  tracking_precision: 0.001

gate:
  min_gap_pp: 10.0
  alpha: 0.05
  min_effect_size: 0.5

checkpointing:
  enabled: true
  frequency: 10  # Save every 10 programs
  output_dir: results/checkpoints/

logging:
  level: INFO
  log_file: results/experiment_log.md
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Compute Budget Tracker | Implement token/time tracking with fairness validation | 8 | dataclass(2) + tracking(3) + fairness(2) + fork(1) |
| C-2 | Self-Consistency Baseline | Implement N-sample generation + selection strategies | 14 | sampling loop(4) + best-of-N(3) + voting(4) + integration(3) |
| C-3 | Hybrid Baseline | Implement sample-then-refine strategy | 11 | sample phase(3) + refinement phase(4) + budget allocation(2) + integration(2) |
| C-4 | Experiment Runner | Orchestrate 2-stage execution with checkpointing | 16 | calibration(4) + test set execution(5) + checkpoint(3) + resume(2) + error handling(2) |
| C-5 | Statistical Analysis | Implement 4 criteria tests + gate decision | 15 | paired t-test(4) + effect size(3) + fairness check(3) + per-program(3) + gate logic(2) |
| C-6 | Visualization | Generate 5 compute-matched plots | 13 | comparison plot(3) + heatmap(3) + scatter(3) + histogram(2) + hybrid plot(2) |
| C-7 | Report Generation | Auto-generate 04_validation.md + state update | 9 | report template(4) + state update(2) + JSON export(2) + figure integration(1) |
| C-8 | Integration & Testing | End-to-end validation with error recovery | 12 | orchestration(3) + validation set run(3) + test set run(3) + error recovery(3) |

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): [C-2, C-4, C-5]
- Medium (9-13): [C-1, C-3, C-6, C-7, C-8]
- Low (4-8): []

**Total Complexity:** 98 points (8 tasks)

---

## Reuse Strategy from H-M1

### Components to Reuse (No Modification)

| Component | From H-M1 | Usage in H-C1 |
|-----------|-----------|---------------|
| SpecificationGenerator | `llm_client.py` | Used by all 3 baselines for ACSL generation |
| FramaCVerifier | `verifier.py` | Used by all 3 baselines for verification |
| FeedbackExtractor | `feedback_parser.py` | Used by Baseline 1 (IterativeFeedback) |
| IterativeRefinementLoop | `refinement_loop.py` | Core of Baseline 1, used in Hybrid phase 2 |
| DatasetManager | `dataset.py` | Load validation + test sets |
| MetricsTracker | `metrics.py` | Track per-iteration metrics (optional) |

### Components to Build New

| Component | Reason |
|-----------|--------|
| ComputeBudgetTracker | H-M1 doesn't track compute budgets |
| SelfConsistencyBaseline | New baseline not in H-M1 |
| HybridBaseline | New baseline not in H-M1 |
| ExperimentRunner | Different orchestration (2-stage, 3 baselines) |
| StatisticalAnalyzer | Different tests (paired t-test, effect size, fairness) |
| ComputeMatchedVisualizer | Different plots (scatter, gap distribution) |

### Import Strategy

**Approach:** Direct imports from h-m1 code directory.

```python
# h-c1/src/baselines/iterative_feedback.py
import sys
from pathlib import Path

# Add h-m1 code to Python path
h_m1_code_path = Path(__file__).parent.parent.parent.parent / "h-m1" / "code" / "code" / "src"
sys.path.insert(0, str(h_m1_code_path))

from llm_client import SpecificationGenerator, ACSLSpec
from verifier import FramaCVerifier, VerificationResult
from refinement_loop import IterativeRefinementLoop
from dataset import DatasetManager, Program
from feedback_parser import FeedbackExtractor, StructuredFeedback
```

**Alternative (if path manipulation is problematic):** Copy h-m1 modules to h-c1/src/utils/ and import locally.

---

## Parallelization Strategy

### Program-Level Parallelization

**Approach:** Parallelize across programs, NOT across baselines (to ensure compute fairness).

**Rationale:**
- Budget matching requires sequential execution (Baseline 1 → compute budget → Baseline 2 with N)
- Independent programs can run in parallel
- API rate limits constrain parallelism

**Implementation:**
```python
# src/core/experiment_runner.py
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

def run_test_set_evaluation(self, test_programs, avg_budget, N):
    max_workers = min(4, multiprocessing.cpu_count())  # API rate limit
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(self._run_single_program, prog, avg_budget, N): prog
            for prog in test_programs
        }
        
        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            # Checkpoint every 10 programs
            if len(results) % 10 == 0:
                self.checkpoint_manager.save_checkpoint(results, {...})
    
    return ExperimentResults(program_results=results, ...)
```

**Rate Limiting:** Use semaphore to limit concurrent LLM API calls.

---

## Error Handling and Logging

### Error Recovery Strategy

**Level 1: LLM API Failures**
```python
# src/baselines/self_consistency.py
def _generate_samples(self, program, N, budget_tracker):
    samples = []
    for i in range(N):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                spec = self.llm_client.generate_initial_spec(program.code)
                budget_tracker.record_llm_call(...)
                samples.append(spec)
                break
            except APIError as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to generate sample {i} for {program.id}: {e}")
                    # Use empty spec as fallback
                    samples.append(ACSLSpec(annotated_code=program.code, ...))
    return samples
```

**Level 2: Verifier Crashes**
```python
# src/baselines/iterative_feedback.py
def run(self, program, budget_tracker):
    try:
        return self.refinement_loop.synthesize(program, budget_tracker)
    except VerifierCrashError as e:
        logger.error(f"Verifier crashed on {program.id}: {e}")
        return BaselineResult(
            program_id=program.id,
            discharge_rate=0.0,
            error="verifier_crash",
            ...
        )
```

**Level 3: Checkpoint Recovery**
```python
# src/core/experiment_runner.py
def run_test_set_evaluation(self, test_programs, avg_budget, N):
    if self.checkpoint_manager.checkpoint_exists():
        completed_results, metadata = self.checkpoint_manager.load_checkpoint()
        completed_ids = {r.program_id for r in completed_results}
        remaining_programs = [p for p in test_programs if p.id not in completed_ids]
        logger.info(f"Resuming from checkpoint: {len(completed_results)} programs done")
    else:
        completed_results = []
        remaining_programs = test_programs
    
    # Run remaining programs
    new_results = self._run_programs(remaining_programs, avg_budget, N)
    all_results = completed_results + new_results
    
    return ExperimentResults(program_results=all_results, ...)
```

### Logging Strategy

**Structured Logging:**
```python
# src/main.py
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('results/experiment_log.md'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('h-c1-experiment')

# Log key events
logger.info(f"Stage 1: Calibration started (15 validation programs)")
logger.info(f"Average budget: {avg_budget.total_tokens} tokens, {avg_budget.verifier_time_seconds}s")
logger.info(f"Computed N={N} for self-consistency")
logger.info(f"Stage 2: Test set evaluation started (50 programs)")
logger.info(f"Checkpoint saved: 10 programs completed")
logger.info(f"Budget violation: Program {program_id} exceeded 110% token budget")
logger.info(f"Gate decision: SATISFIED (all 4 criteria met)")
```

---

## Integration Points

### Frama-C Integration (Reuse from H-M1)

**FramaCVerifier API:**
```python
# From h-m1/code/code/src/verifier.py
verifier = FramaCVerifier(timeout_per_obligation=10)
result = verifier.verify(program.code, acsl_spec.annotated_code)

# Returns VerificationResult:
# - total_obligations: int
# - proved_obligations: int
# - proof_discharge_rate: float
# - obligations: List[ProofObligation]
```

**Time Tracking:** FramaCVerifier internally measures execution time, accessible via `result.execution_time`.

### LLM API Integration (Reuse from H-M1)

**SpecificationGenerator API:**
```python
# From h-m1/code/code/src/llm_client.py
llm_client = SpecificationGenerator(api_key=api_key, model="claude-opus-4-5")

# Initial generation
spec = llm_client.generate_initial_spec(
    c_code=program.code,
    temperature=0.7  # For sampling
)

# Refinement with feedback
refined_spec = llm_client.refine_spec(
    current_spec=spec,
    feedback=structured_feedback,
    temperature=0.2  # For refinement
)
```

**Token Tracking:** LLM client returns token counts in response metadata, captured by ComputeBudgetTracker.

### Dataset Integration (Reuse from H-M1)

**DatasetManager API:**
```python
# From h-m1/code/code/src/dataset.py
dataset_manager = DatasetManager(benchmark_name="acsl-by-example")

# Load validation set (15 programs)
validation_programs = dataset_manager.load_validation_set()

# Load test set (50 programs)
test_programs = dataset_manager.load_test_set()

# Each Program object:
# - id: str
# - code: str
# - gold_spec: str
# - complexity: str
# - proof_obligations: int
```

---

## Validation Strategy

### Unit Tests

**Test Coverage:**
- ComputeBudgetTracker: Test tracking, exceeds_target, fork
- SelfConsistencyBaseline: Test sampling loop, best-of-N selection
- HybridBaseline: Test budget allocation, phase transitions
- StatisticalAnalyzer: Test t-test, effect size, fairness validation with mock data

### Integration Tests

**End-to-End Test:**
1. 5 programs × 3 baselines = 15 trials
2. Expected: All trials complete, compute budgets within tolerance
3. Verify: Statistical tests run, gate decision made, plots generated

### Validation Criteria (Phase 4)

**Code Validation:**
- All tests pass
- Imports from h-m1 resolve correctly
- No hardcoded API keys/paths

**Experiment Validation:**
- Baseline 1 reproduces h-m1 discharge rates on validation set (±2pp)
- Baseline 2 budget within 10% of Baseline 1
- All 5 plots generated successfully
- 04_validation.md contains gate decision

---

**Architecture Version:** 1.0  
**Status:** Ready for Phase 4 Implementation  
**Next Step:** Phase 4 Coder implements modules following this specification
