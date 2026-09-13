# Architecture: h-m1 (NL Hint Ablation)

**Generated**: 2026-08-20  
**Hypothesis**: NL hint removal drops LLM success by 25-35pp  
**Type**: MECHANISM  
**Gate**: MUST_WORK

Applied: Parallel evaluation pattern, checkpoint recovery

---

## System Architecture

```
HuggingFace Dataset (miniF2F-v2c)
    ↓
DataLoader (extract 244 problems)
    ↓
Preprocessor (regex NL removal) → [Pilot: 20 samples] → Go/No-Go
    ↓
Lean File Generator
    ├─→ baseline.lean (NL-intact)
    └─→ ablated.lean (NL-stripped)
    ↓
LeanCopilot Evaluator (8 workers, @32 sampling, 300s timeout)
    ├─→ baseline_results.jsonl
    └─→ ablated_results.jsonl
    ↓
Statistical Analyzer (McNemar, bootstrap CI)
    ↓
Gate Decision (PASS/FAIL/INCONCLUSIVE)
```

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: h-e1 provides worker pattern reference only (lean-auto vs LeanCopilot different APIs)

---

## Module Interfaces

### 1. DataLoader (`src/loader.py`)

**Dependencies**: datasets (HuggingFace)

```python
from dataclasses import dataclass
from typing import List

@dataclass
class Problem:
    id: str
    formal_statement: str
    informal_statement: str
    source: str

def load_minif2f_v2c(split: str = "test") -> List[Problem]: ...
```

---

### 2. Preprocessor (`src/preprocessor.py`)

**Dependencies**: re

```python
def strip_nl_hints(lean_code: str) -> str: ...
def verify_type_check(lean_file: str, timeout: int = 60) -> tuple[bool, str]: ...
def generate_ablated_dataset(problems: List[Problem], output_path: str) -> None: ...
```

---

### 3. PilotValidator (`src/pilot.py`)

**Dependencies**: loader, preprocessor

```python
@dataclass
class PilotDecision:
    go: bool
    type_check_failures: int
    delta: float
    reason: str

def run_pilot(n_samples: int = 20, seed: int = 42) -> PilotDecision: ...
```

---

### 4. LeanCopilotEvaluator (`src/evaluator.py`)

**Dependencies**: subprocess, multiprocessing

```python
@dataclass
class EvalResult:
    problem_id: str
    condition: str
    success: bool
    wall_time: float
    tactics_used: Optional[int]
    error_type: Optional[str]

def evaluate_problem(problem: Problem, timeout: int = 300, budget: int = 32) -> EvalResult: ...
def run_parallel(problems: List[Problem], condition: str, workers: int = 8, checkpoint_dir: str = "./checkpoints") -> List[EvalResult]: ...
```

---

### 5. StatisticalAnalyzer (`src/analyzer.py`)

**Dependencies**: numpy, scipy.stats, matplotlib

```python
@dataclass
class ComparisonStats:
    baseline_success_rate: float
    ablated_success_rate: float
    delta: float
    mcnemar_statistic: float
    p_value: float
    ci_95_low: float
    ci_95_high: float
    verdict: str

def compute_mcnemar(baseline: List[bool], ablated: List[bool]) -> tuple[float, float]: ...
def bootstrap_ci(baseline: List[bool], ablated: List[bool], n_resamples: int = 10000, seed: int = 42) -> tuple[float, float]: ...
def gate_decision(stats: ComparisonStats) -> str: ...
def generate_plots(stats: ComparisonStats, output_dir: str) -> None: ...
```

---

### 6. Main Pipeline (`src/main.py`)

**Dependencies**: All modules above

```python
def main():
    # Load dataset
    # Run pilot
    # Generate full datasets
    # Evaluate both conditions
    # Statistical analysis
    # Gate decision
    ...
```

---

## Data Flow

**Phase 1: Dataset Preparation**
1. `load_minif2f_v2c()` → 244 Problem objects
2. `strip_nl_hints()` on each formal_statement
3. Pilot: sample 20, validate type-check, measure Δ

**Phase 2: Evaluation**
1. Generate `baseline.lean` (original), `ablated.lean` (stripped)
2. `run_parallel()` on both conditions (8 workers each)
3. Write `baseline_results.jsonl`, `ablated_results.jsonl`

**Phase 3: Analysis**
1. Load results → List[bool] success arrays
2. `compute_mcnemar()` → (χ², p-value)
3. `bootstrap_ci()` → (CI_low, CI_high)
4. `gate_decision()` → PASS/FAIL/INCONCLUSIVE

---

## Error Handling

**Type-Check Failures**: Pilot aborts if >3 failures (escalate fallback)  
**Timeouts**: Kill process after 360s (300s + 60s buffer), log as timeout  
**Worker Crashes**: Checkpoint every 10 problems, resume on restart  
**Dataset Download Failures**: Retry 3 times with exponential backoff

---

## Logging

**Levels**:
- INFO: Pipeline progress (phase start/end, problem counts)
- DEBUG: Per-problem evaluation (LeanCopilot invocation, result)
- WARNING: Pilot Go/No-Go decision, high timeout rate
- ERROR: Type-check failures, worker crashes

**Format**: JSON lines to `logs/h-m1.log`

```json
{"timestamp": "2026-08-20T12:00:00Z", "level": "INFO", "phase": "pilot", "msg": "Go/No-Go decision: GO", "delta": 0.15}
```

---

## Deployment

**Environment**: Single GPU node (A5000 24GB, 32 CPU cores, 128GB RAM)  
**Software**: Lean 4.17.0, LeanCopilot (main), Python 3.9+  
**Runtime**: ~41 hours (pilot: 3h, full: 38h)  
**Output**: `results/` directory with `.jsonl` files, `plots/` with `.png`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup environment | Install Lean 4.17, LeanCopilot, Python deps | 8 | 2+2+2+2 |
| A-2 | Implement data loader | HuggingFace → Problem objects | 6 | 2+1+2+1 |
| A-3 | Implement preprocessor | Regex NL removal + type-check validation | 10 | 3+2+3+2 |
| A-4 | Implement pilot validator | 20-sample validation, Go/No-Go logic | 9 | 2+2+3+2 |
| A-5 | Implement LeanCopilot evaluator | Parallel worker harness, checkpointing | 16 | 4+4+4+4 |
| A-6 | Implement statistical analyzer | McNemar, bootstrap CI, plots | 12 | 3+3+3+3 |
| A-7 | Run pilot experiment | Execute pilot, validate Go/No-Go | 7 | 2+2+2+1 |
| A-8 | Run full evaluation | 244 problems × 2 conditions | 14 | 4+4+4+2 |
| A-9 | Generate validation report | 04_validation.md with plots and gate decision | 10 | 3+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5, A-8], Medium(9-13): [A-3, A-4, A-6, A-9], Low(4-8): [A-1, A-2, A-7]

---

## Configuration

```python
# config.py
DATASET_NAME = "roozbeh-yz/miniF2F_v2"
DATASET_CONFIG = "v2c"
DATASET_SPLIT = "test"
LEAN_VERSION = "4.17.0"
LEANCOPILOT_TACTIC = "search_proof"
SAMPLING_BUDGET = 32
TIMEOUT_SECONDS = 300
N_WORKERS = 8
PILOT_N_SAMPLES = 20
PILOT_MAX_FAILURES = 3
PILOT_MIN_DELTA = 0.05
MCNEMAR_ALPHA = 0.05
BOOTSTRAP_RESAMPLES = 10000
CHECKPOINT_FREQ = 10
RANDOM_SEED = 42
```

---

## Validation Criteria

**Technical**:
- Pilot: ≤3 type-check failures, Δ ≥ 5%
- Full: 0 compilation errors for both datasets
- Full: 244 problems evaluated per condition

**Scientific**:
- Primary: 25% ≤ Δ ≤ 35%
- Falsification: Δ < 10%
- Statistical: p < 0.05
- Robustness: 95% CI excludes 0

**Gate**:
- PASS: Δ ≥ 25% AND p < 0.05
- FAIL: Δ < 10% OR p ≥ 0.05
- INCONCLUSIVE: 10% ≤ Δ < 25%
