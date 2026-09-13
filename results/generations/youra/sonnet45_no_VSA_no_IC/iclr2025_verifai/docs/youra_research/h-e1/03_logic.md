# Logic Specification: H-E1
# lean-auto Baseline Measurement on miniF2F

**Version**: 1.0  
**Date**: 2026-08-20  
**Hypothesis**: h-e1 (EXISTENCE - PoC)  
**Complexity Budget**: 120 subtasks

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing codebase  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - baseline measurement experiment

---

## Applied Patterns

**Applied**: Standard Python subprocess + regex parsing + scipy.stats

---

## Core Algorithms

### A-1: Problem Loading [Complexity: 2, Budget: 2]

Parse miniF2F Test.lean to extract theorem statements.

**API Signatures**

```python
from dataclasses import dataclass
from typing import List
import re

@dataclass
class Problem:
    """miniF2F problem."""
    id: str
    statement: str
    source: str  # AMC/AIME/IMO

def load_minif2f_problems(filepath: str) -> List[Problem]:
    """Load problems from Test.lean. Returns: 244 problems"""
    ...

def extract_source(name: str) -> str:
    """Extract source from name. 'amc12a_2000_p1' -> 'AMC'"""
    ...
```

**Pseudo-code**

```
1. Read Test.lean
2. Regex: r'theorem\s+(\w+)\s*:(.+?)(?=theorem|$)'
3. For each match: create Problem(id=name, statement=stmt, source=extract_source(name))
4. Return list
```

**Subtasks [2/2 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | File parsing | Read and regex extract |
| L-1-2 | Source extraction | Parse name for AMC/AIME/IMO |

---

### A-2: Prover Invocation [Complexity: 5, Budget: 8]

Execute lean-auto with timeout, capture outcome and logs.

**API Signatures**

```python
from typing import Optional
import subprocess
import time

@dataclass
class ProverResult:
    """Single problem result."""
    problem_id: str
    source: str
    outcome: str  # "solved" | "timeout" | "error"
    time_s: float
    tactic_count: Optional[int]
    trace_log: Optional[str]

def evaluate_single_problem(
    problem: Problem,
    timeout: int = 300
) -> ProverResult:
    """Run lean-auto on problem. timeout in seconds."""
    ...

def create_lean_script(problem: Problem) -> str:
    """Generate Lean script. Returns: script text"""
    ...
```

**Pseudo-code**

```
1. script = create_lean_script(problem)  # Import + set_option + theorem
2. Write to /tmp/{problem.id}.lean
3. proc = subprocess.run(["lean", path], timeout=timeout, capture_output=True)
4. If returncode == 0: outcome = "solved", extract tactic_count
5. If TimeoutExpired: outcome = "timeout", tactic_count = None
6. If returncode != 0: outcome = "error", tactic_count = None
7. Return ProverResult(...)
```

**Subtasks [8/8 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Script generation | Create Lean file with imports |
| L-2-2 | Timeout enforcement | subprocess.run with timeout |
| L-2-3 | SIGTERM/SIGKILL | Handle timeout with proc.kill() |
| L-2-4 | Log capture | stderr/stdout to trace_log |
| L-2-5 | Outcome classification | Parse returncode |
| L-2-6 | Timing | Wall-clock measurement |
| L-2-7 | Temp file cleanup | Remove /tmp/*.lean |
| L-2-8 | Error handling | Retry on infrastructure crash |

---

### A-3: Tactic Count Extraction [Complexity: 4, Budget: 6]

Parse trace logs to count ATP solver invocations.

**API Signatures**

```python
def extract_tactic_count(trace_log: Optional[str]) -> Optional[int]:
    """Count tactic evaluations from trace.auto logs. Returns: count or None"""
    ...

def validate_extraction(
    problems: List[ProverResult],
    sample_size: int = 5
) -> bool:
    """Manual validation on sample. Returns: True if 80%+ accuracy"""
    ...
```

**Pseudo-code**

```
1. If trace_log is None: return None
2. Primary: matches = re.findall(r'\[auto\.native\] Invoking', trace_log)
3. If len(matches) > 0: return len(matches)
4. Fallback: mono_steps = re.findall(r'\[auto\.mono\] Instantiating', trace_log)
5. Return len(mono_steps) if mono_steps else None
```

**Subtasks [6/6 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Regex pattern | Match ATP invocations |
| L-3-2 | Fallback pattern | Monomorphization steps |
| L-3-3 | Count logic | Unique invocations |
| L-3-4 | Validation | Manual check 5 samples |
| L-3-5 | Accuracy check | Ensure 80%+ match |
| L-3-6 | None handling | Missing logs |

---

### A-4: Parallel Execution [Complexity: 3, Budget: 5]

Distribute 244 problems across 8 workers with checkpointing.

**API Signatures**

```python
from multiprocessing import Pool
from typing import Callable

def worker_with_checkpoint(
    problems: List[Problem],
    worker_id: int,
    checkpoint_freq: int = 10
) -> List[ProverResult]:
    """Process problems with checkpointing. Returns: results"""
    ...

def save_checkpoint(worker_id: int, results: List[ProverResult]) -> None:
    """Save progress to /data/checkpoints/worker_{id}.json"""
    ...

def load_checkpoint(worker_id: int) -> List[ProverResult]:
    """Load checkpoint. Returns: results or empty list"""
    ...

def run_parallel_evaluation(
    problems: List[Problem],
    n_workers: int = 8
) -> List[ProverResult]:
    """Run evaluation on worker pool. Returns: all results"""
    ...
```

**Pseudo-code**

```
1. chunk_size = len(problems) // n_workers
2. chunks = [problems[i:i+chunk_size] for i in range(0, len(problems), chunk_size)]
3. with Pool(n_workers) as pool:
4.     all_results = pool.map(worker_with_checkpoint, chunks)
5. Flatten all_results
6. Return results
```

**Subtasks [5/5 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Partitioning | Split 244 problems into 8 chunks |
| L-4-2 | Worker spawn | multiprocessing.Pool |
| L-4-3 | Checkpoint save | JSON dump every 10 problems |
| L-4-4 | Checkpoint load | Recovery on restart |
| L-4-5 | Result aggregation | Flatten worker outputs |

---

### A-5: Statistical Analysis [Complexity: 3, Budget: 5]

Compute success rate with Wilson CI and tactic count stats.

**API Signatures**

```python
from scipy.stats import binomtest
import numpy as np

@dataclass
class Statistics:
    """Experiment statistics."""
    success_rate: float
    ci_95_low: float
    ci_95_high: float
    solved_count: int
    timeout_count: int
    error_count: int
    mean_tactics: Optional[float]
    std_tactics: Optional[float]
    cv_tactics: Optional[float]

def compute_metrics(results: List[ProverResult]) -> Statistics:
    """Compute all metrics. Returns: statistics"""
    ...

def wilson_ci(n_solved: int, n_total: int, confidence: float = 0.95) -> tuple:
    """Wilson score CI. Returns: (low, high)"""
    ...
```

**Pseudo-code**

```
1. n_solved = sum(1 for r in results if r.outcome == "solved")
2. n_total = len(results)
3. success_rate = n_solved / n_total
4. ci = binomtest(n_solved, n_total).proportion_ci(confidence_level=0.95)
5. tactic_counts = [r.tactic_count for r in results if r.tactic_count is not None]
6. mean_tactics = np.mean(tactic_counts) if tactic_counts else None
7. std_tactics = np.std(tactic_counts) if tactic_counts else None
8. Return Statistics(...)
```

**Subtasks [5/5 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Success rate | Count solved / total |
| L-5-2 | Wilson CI | binomtest confidence interval |
| L-5-3 | Tactic stats | Mean, std, CV |
| L-5-4 | Timeout/error rates | Count by outcome |
| L-5-5 | Source stratification | Group by AMC/AIME/IMO |

---

### A-6: Validation Gates [Complexity: 2, Budget: 4]

Check quality gates before accepting results.

**API Signatures**

```python
@dataclass
class ValidationResult:
    """Validation outcome."""
    passed: bool
    failed_gates: List[str]
    warnings: List[str]

def validate_completeness(results: List[ProverResult]) -> bool:
    """All 244 problems evaluated. Returns: True if complete"""
    ...

def validate_error_rate(results: List[ProverResult], threshold: float = 0.05) -> bool:
    """Error rate < 5%. Returns: True if acceptable"""
    ...

def validate_tactic_extraction(results: List[ProverResult], threshold: float = 0.8) -> bool:
    """Tactic count captured for ≥80% solved. Returns: True if valid"""
    ...

def run_validation_gates(results: List[ProverResult]) -> ValidationResult:
    """Run all gates. Returns: validation result"""
    ...
```

**Pseudo-code**

```
1. Check len(results) == 244
2. error_rate = sum(r.outcome == "error" for r in results) / len(results)
3. Check error_rate < 0.05
4. solved = [r for r in results if r.outcome == "solved"]
5. tactic_captured = sum(1 for r in solved if r.tactic_count is not None) / len(solved)
6. Check tactic_captured >= 0.8
7. Return ValidationResult(passed=all_checks_pass, failed_gates=[], warnings=[])
```

**Subtasks [4/4 used]**

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Completeness check | 244 problems evaluated |
| L-6-2 | Error rate check | < 5% errors |
| L-6-3 | Tactic extraction check | ≥80% coverage |
| L-6-4 | Reproducibility check | Rerun 10% sample |

---

## Edge Case Handling

### E-1: Lean REPL Crash

**Detection**: subprocess returns non-zero with infrastructure error message  
**Handling**: Retry up to 3 times with fresh environment  
**Fallback**: Log as "error" and continue  
**Impact**: Acceptable if < 5% of problems

### E-2: Timeout Ineffective

**Detection**: Problem runs beyond timeout + 10s grace period  
**Handling**: SIGKILL at timeout + 10s (subprocess.kill())  
**Validation**: Check elapsed time < timeout + 15s  
**Mitigation**: OS-level timeout enforcement, not lean-auto internal

### E-3: Missing Trace Logs

**Detection**: trace_log is None or empty for solved problem  
**Handling**: Use fallback proxy (wall-clock time / 30s)  
**Validation**: Flag in logs for manual review  
**Impact**: Affects H-C1 budget setting, acceptable if < 20%

### E-4: ATP Backend Failure

**Detection**: lean-auto error message contains "ATP", "Z3", "solver"  
**Handling**: lean-auto fallback to other backends (automatic)  
**Logging**: Record backend failure in error_type  
**Mitigation**: None - lean-auto handles internally

### E-5: Incomplete Checkpoint

**Detection**: Checkpoint file corrupted or missing  
**Handling**: Restart from last valid checkpoint  
**Validation**: Check checkpoint JSON schema before load  
**Mitigation**: Write to temp file, then atomic rename

---

## Pilot Run Validation

**Before Full Run**: Execute on N=20 random sample

**Quality Checks**:

| Check | Criterion | Action if Failed |
|-------|-----------|------------------|
| Solves | 2-5 problems (10-25%) | Debug lean-auto setup |
| Errors | < 1 problem (5%) | Investigate infrastructure |
| Logs | All captured | Fix log capture |
| Tactic count | Extracted for ≥80% solves | Validate regex patterns |
| Crashes | 0 worker crashes | Fix resource limits |

**Gate Decision**:
- PASS: All checks pass → Proceed to full run
- FAIL: Any check fails → Debug before full run

---

## Data Flow

```
Test.lean
  → load_minif2f_problems()
  → List[Problem] (244)
  → run_parallel_evaluation(n_workers=8)
    → worker_with_checkpoint(problems, worker_id)
      → For each problem:
        → evaluate_single_problem(problem, timeout=300)
          → create_lean_script()
          → subprocess.run(lean, timeout=300)
          → extract_tactic_count(trace_log)
          → Return ProverResult
        → save_checkpoint(worker_id, results) every 10 problems
      → Return List[ProverResult]
  → Aggregate all worker results
  → compute_metrics(results)
  → run_validation_gates(results)
  → Save results.csv + summary.json
```

---

## Configuration Constants

```python
# Evaluation settings
TIMEOUT_SECONDS = 300
TIMEOUT_GRACE_SECONDS = 10
N_WORKERS = 8
CHECKPOINT_FREQ = 10

# Validation thresholds
MAX_ERROR_RATE = 0.05
MIN_TACTIC_EXTRACTION_RATE = 0.80
EXPECTED_SUCCESS_RATE_MIN = 0.10
EXPECTED_SUCCESS_RATE_MAX = 0.25

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5

# Paths
MINIF2F_PATH = "miniF2F/Minif2f/Test.lean"
CHECKPOINT_DIR = "/data/checkpoints"
RESULTS_CSV = "/data/h-e1/results.csv"
SUMMARY_JSON = "/data/h-e1/summary.json"
```

---

## Lean Script Template

```lean
import Minif2f.Test
import Auto

set_option auto.smt false
set_option auto.tptp false
set_option auto.native true
set_option trace.auto true
set_option trace.auto.mono true

-- Target theorem: {problem_id}
example : {statement} := by
  auto
```

---

## Output Schema

**results.csv**:
```
problem_id,source,outcome,time_s,tactic_count,proof_size,atp_backend
test_001,AMC,solved,12.3,8,156,Duper
test_002,AIME,timeout,300.0,,,
test_003,IMO,error,1.2,,,TypeError
```

**summary.json**:
```json
{
  "hypothesis_id": "h-e1",
  "dataset": {
    "name": "miniF2F Lean 4 Test",
    "size": 244
  },
  "results": {
    "success_rate": 0.156,
    "ci_95": [0.115, 0.203],
    "solved_count": 38,
    "timeout_count": 180,
    "error_count": 26
  },
  "tactic_count": {
    "mean": 9.2,
    "median": 8.0,
    "std": 4.1,
    "cv": 0.45,
    "range": [3, 22]
  },
  "execution": {
    "total_time_hours": 20.3,
    "mean_time_per_problem": 300.2
  }
}
```

---

## Complexity Summary

**Total Budget**: 120 subtasks  
**Allocated**:

| Module | Complexity | Subtasks |
|--------|-----------|----------|
| A-1: Problem Loading | 2 | 2 |
| A-2: Prover Invocation | 5 | 8 |
| A-3: Tactic Extraction | 4 | 6 |
| A-4: Parallel Execution | 3 | 5 |
| A-5: Statistical Analysis | 3 | 5 |
| A-6: Validation Gates | 2 | 4 |
| **Total** | **19** | **30** |

**Remaining**: 90 subtasks (reserved for Phase 4 integration/debugging)

---

## Dependencies

**External**:
- Lean 4.15.0 (via elan)
- lean-auto (leanprover-community/lean-auto)
- miniF2F (google-deepmind/miniF2F)

**Python**:
- Python 3.10+
- scipy (binomtest, Wilson CI)
- numpy (statistics)
- pandas (DataFrame for results)
- multiprocessing (parallel workers)

**System**:
- 64 CPU cores (8 workers × 8 cores)
- 128GB RAM (8 workers × 16GB)
- 50GB disk (miniF2F + mathlib + logs)

---

## Self-Validation Checklist

- [x] No ASCII diagrams (text only)
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes N/A (not ML)
- [x] Subtask count within budget (30/120)
- [x] Total length < 600 lines
- [x] Codebase Analysis section included
- [x] Green-field project (Serena skip acceptable)
- [x] API signatures copy-paste ready
- [x] Edge cases documented
- [x] Validation logic specified

---

**Next Phase**: Phase 4 (Implementation)  
**Output**: Evaluation harness code + pilot run results
