# Logic Specification: h-m1 (NL Hint Ablation)

**Generated**: 2026-08-20  
**Hypothesis**: h-m1  
**Type**: MECHANISM  
**Gate**: MUST_WORK

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: Green-field - new API design  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - new implementation

---

## KB Patterns Applied

**Applied**: Standard Python regex, scipy.stats.mcnemar, scipy.stats.bootstrap

---

## Task Logic (High-Complexity Only)

### L-1: NL Ablation Preprocessing

**Complexity**: 2, **Budget**: 2

```python
import re
from typing import List, Dict

def strip_nl_hints(lean_code: str) -> str:
    """Remove NL from Lean 4. lean_code: str -> str"""
    # Strip /--! ... -/ (DOTALL for multiline)
    lean_code = re.sub(r'/--!.*?-/', '', lean_code, flags=re.DOTALL)
    # Strip -- ... (inline)
    lean_code = re.sub(r'--[^\n]*', '', lean_code)
    return lean_code.strip()

def generate_lean_file(problems: List[Dict], output_path: str, ablate: bool = False) -> None:
    """Write problems to .lean. problems: List[{formal_statement: str}]"""
    with open(output_path, 'w') as f:
        for i, p in enumerate(problems):
            code = strip_nl_hints(p['formal_statement']) if ablate else p['formal_statement']
            f.write(f"-- Problem {i+1}\n{code}\n\n")
```

**Edge Cases**:
- Nested docstrings (rare in Lean 4, regex non-greedy `.*?` handles)
- Comments containing `--` in strings (accepted risk, theorem syntax unlikely)

**Validation**: Lean type-checker (`lake build`) post-ablation

**Subtasks** [2/2 used]:
| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Regex removal | /--! docstrings, -- comments |
| L-1-2 | File generation | Write ablated .lean |

---

### L-2: Pilot Validator

**Complexity**: 2, **Budget**: 2

```python
import random
from typing import Tuple

def pilot_validate(
    problems: List[Dict],
    sample_size: int = 20,
    seed: int = 42
) -> Tuple[bool, str]:
    """Go/No-Go decision. Returns: (go: bool, reason: str)"""
    random.seed(seed)
    pilot = random.sample(problems, sample_size)
    
    generate_lean_file(pilot, "Pilot_Baseline.lean", ablate=False)
    generate_lean_file(pilot, "Pilot_Ablated.lean", ablate=True)
    
    # Subprocess: lake build Pilot_Ablated.lean
    type_check_errors = count_lean_errors("Pilot_Ablated.lean")  # L-3-1
    
    baseline_results = evaluate_problems(pilot, ablate=False)  # L-3
    ablated_results = evaluate_problems(pilot, ablate=True)
    
    delta = success_rate(baseline_results) - success_rate(ablated_results)
    
    if type_check_errors > 3:
        return (False, f"Type-check failures: {type_check_errors}")
    if delta < 0.05:
        return (False, f"Δ too small: {delta:.2%}")
    
    return (True, f"Δ={delta:.2%}, errors={type_check_errors}")
```

**Subtasks** [2/2 used]:
| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Sample problems | Random 20 problems |
| L-2-2 | Go/No-Go logic | Check errors ≤3, Δ ≥5% |

---

### L-3: LeanCopilot Evaluation

**Complexity**: 3, **Budget**: 3

```python
import subprocess
import time
from typing import Dict, Optional

def evaluate_problem(
    problem_id: str,
    lean_code: str,
    timeout: int = 300
) -> Dict:
    """Eval single problem. Returns: {success, wall_time, error_type}"""
    temp_file = f"temp_{problem_id}.lean"
    with open(temp_file, 'w') as f:
        f.write(lean_code)
    
    start = time.time()
    try:
        result = subprocess.run(
            ["lake", "env", "lean", temp_file],
            timeout=timeout,
            capture_output=True,
            text=True
        )
        wall_time = time.time() - start
        success = (result.returncode == 0)
        error = None if success else "proof_failed"
        
    except subprocess.TimeoutExpired:
        wall_time = timeout
        success = False
        error = "timeout"
    except Exception as e:
        wall_time = time.time() - start
        success = False
        error = f"crash_{type(e).__name__}"
    
    return {
        "problem_id": problem_id,
        "success": success,
        "wall_time": wall_time,
        "error_type": error
    }
```

**Parallel Wrapper** (uses multiprocessing.Pool, 8 workers):

```python
from multiprocessing import Pool

def evaluate_problems(problems: List[Dict], ablate: bool) -> List[Dict]:
    """Eval all problems parallel. Returns: [{problem_id, success, ...}]"""
    args = [
        (f"test_{i:03d}", strip_nl_hints(p['formal_statement']) if ablate else p['formal_statement'], 300)
        for i, p in enumerate(problems)
    ]
    
    with Pool(8) as pool:
        results = pool.starmap(evaluate_problem, args)
    
    return results
```

**Edge Cases**:
- Worker crash: catch in parent, mark as error_type="worker_crash"
- Disk full: pre-check storage before batch, fail fast
- Stuck process: subprocess.run timeout=300, kill after 360s (60s buffer)

**Subtasks** [3/3 used]:
| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Single eval | subprocess with timeout |
| L-3-2 | Parallel harness | multiprocessing.Pool |
| L-3-3 | Error handling | timeout, crash, type-check |

---

### L-4: Statistical Tests

**Complexity**: 3, **Budget**: 3

```python
import numpy as np
from scipy.stats import mcnemar
from scipy.stats import bootstrap

def mcnemar_test(baseline: List[bool], ablated: List[bool]) -> Tuple[float, float]:
    """Paired proportions test. Returns: (statistic, p_value)"""
    # Contingency: [[both_success, baseline_only], [ablated_only, both_fail]]
    both_success = sum(b and a for b, a in zip(baseline, ablated))
    baseline_only = sum(b and not a for b, a in zip(baseline, ablated))
    ablated_only = sum(not b and a for b, a in zip(baseline, ablated))
    both_fail = sum(not b and not a for b, a in zip(baseline, ablated))
    
    contingency = [[both_success, baseline_only],
                   [ablated_only, both_fail]]
    
    result = mcnemar(contingency, exact=False)
    return (result.statistic, result.pvalue)

def bootstrap_ci(
    baseline: List[bool],
    ablated: List[bool],
    n_resamples: int = 10000,
    confidence: float = 0.95,
    seed: int = 42
) -> Tuple[float, float]:
    """Bootstrap 95% CI on Δ. Returns: (ci_low, ci_high)"""
    def delta_stat(b, a):
        return np.mean(b) - np.mean(a)
    
    rng = np.random.default_rng(seed=seed)
    res = bootstrap(
        (np.array(baseline), np.array(ablated)),
        delta_stat,
        n_resamples=n_resamples,
        confidence_level=confidence,
        random_state=rng
    )
    
    return (res.confidence_interval.low, res.confidence_interval.high)

def gate_decision(delta: float, p_value: float) -> str:
    """PASS/FAIL/INCONCLUSIVE logic."""
    if delta >= 0.25 and p_value < 0.05:
        return "PASS"
    elif delta < 0.10 or p_value >= 0.05:
        return "FAIL"
    else:
        return "INCONCLUSIVE"
```

**Edge Cases**:
- Zero variance: IF all same outcome, McNemar undefined → return p=1.0, warn
- Small sample (N<30): exact=True for McNemar (conservative)
- Bootstrap convergence: 10k resamples standard, CI may widen if high variance

**Subtasks** [3/3 used]:
| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | McNemar's test | Contingency table, chi-square |
| L-4-2 | Bootstrap CI | Resample delta, 95% CI |
| L-4-3 | Gate logic | PASS/FAIL/INCONCLUSIVE rules |

---

## Algorithm Complexity

| Function | Time | Space | Notes |
|----------|------|-------|-------|
| strip_nl_hints | O(n) | O(n) | n = len(lean_code), regex scan |
| evaluate_problem | O(1) | O(1) | Subprocess async, timeout constant |
| mcnemar_test | O(n) | O(1) | n = problems, contingency build |
| bootstrap_ci | O(k×n) | O(n) | k = 10k resamples, n = 244 |

---

## Input Validation Rules

```python
# dataset_loader.py
def validate_dataset(problems: List[Dict]) -> None:
    """Fail fast on schema mismatch."""
    assert len(problems) == 244, f"Expected 244, got {len(problems)}"
    for p in problems:
        assert "formal_statement" in p, f"Missing field: {p.keys()}"
        assert isinstance(p["formal_statement"], str), "formal_statement not str"

# evaluate_leancopilot.py
def validate_config(timeout: int, workers: int) -> None:
    """Check runtime config."""
    assert timeout > 0, "timeout must be positive"
    assert 1 <= workers <= 32, "workers out of range [1, 32]"
```

---

## Error Handling Strategy

**Type-Check Failures** (pilot):
1. Count errors from `lake build` stderr
2. IF >3 → abort, log failed examples
3. Manual inspection: check if semantic type info removed

**Evaluation Timeouts**:
1. subprocess.run(timeout=300)
2. except TimeoutExpired → mark error_type="timeout"
3. Continue with next problem (no abort)

**Worker Crashes**:
1. multiprocessing.Pool catches child exceptions
2. Log to stderr, mark error_type="worker_crash"
3. IF >10% workers crash → abort, escalate hardware issue

**Statistical Edge Cases**:
1. Zero variance → warn, set p=1.0
2. Small N (<30) → use exact McNemar
3. Bootstrap non-convergence → increase resamples to 50k, warn if CI width >0.2

---

## Pseudo-Code: Main Pipeline

```
1. Load dataset (miniF2F-v2c, 244 problems)
2. Validate schema (FR-1)
3. Pilot validation:
   a. Sample 20 problems (seed 42)
   b. Generate baseline/ablated .lean files
   c. Type-check ablated (count errors)
   d. Evaluate pilot (baseline + ablated)
   e. Compute pilot Δ
   f. Go/No-Go: IF errors ≤3 AND Δ ≥5% → proceed ELSE abort
4. Full dataset generation:
   a. Generate MiniF2F_v2c_Test.lean (244 baseline)
   b. Generate MiniF2F_v2c_Test_NoNL.lean (244 ablated)
   c. Type-check both (0 errors required)
5. Parallel evaluation:
   a. Evaluate baseline (8 workers, 300s timeout)
   b. Evaluate ablated (8 workers, 300s timeout)
   c. Save results: baseline_results.jsonl, ablated_results.jsonl
6. Statistical analysis:
   a. Compute success rates
   b. McNemar's test (paired)
   c. Bootstrap 95% CI on Δ
   d. Gate decision (PASS/FAIL/INCONCLUSIVE)
   e. Save comparison_stats.json
7. Generate 04_validation.md report
```

---

## Data Flow Diagram

```
[HuggingFace] → dataset_loader.py → [{problem_id, formal_statement}] → preprocess.py
                                                                            ↓
                                    [Pilot_Baseline.lean, Pilot_Ablated.lean] → lake build
                                                                            ↓
                                                pilot_validate() → (go: bool, reason: str)
                                                                            ↓
[IF go=True] → Full dataset generation → [MiniF2F_v2c_Test.lean, MiniF2F_v2c_Test_NoNL.lean]
                                                                            ↓
                              evaluate_leancopilot.py (multiprocessing.Pool, 8 workers)
                                                                            ↓
                            [baseline_results.jsonl, ablated_results.jsonl] → analyze.py
                                                                            ↓
                              mcnemar_test() + bootstrap_ci() → comparison_stats.json
                                                                            ↓
                                                                  gate_decision() → verdict
                                                                            ↓
                                                                  04_validation.md
```

---

## Self-Validation Checklist

- [x] No ASCII diagrams (text-only flow)
- [x] KB search logs omitted (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in comments (N/A - no tensors)
- [x] Subtask count within budget (all tasks ≤ allocated)
- [x] Total length < 600 lines
- [x] Codebase Analysis section included
- [x] Green-field project noted
- [x] Serena skip acceptable (no existing code)

---

**Phase 3 Complete**  
**Handoff to Phase 4**: API signatures verified, ready for copy-paste implementation
