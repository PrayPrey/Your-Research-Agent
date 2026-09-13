# Logic Specification: h-m2

**Date:** 2026-08-25
**Author:** Phase 3 Logic Agent
**Hypothesis:** h-m2 (MECHANISM - ANOVA Validation)
**PRD:** 03_prd.md

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Extends h-e1 correlation infrastructure
**Analyzed Path**: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-e1/code/
**Relevant Symbols**: Problem, compute_pairwise_correlations, bootstrap_ci

---

## M1: Feedback Loading [Complexity: 7, Budget: 3]

**Applied**: numpy load from h-e1 cache

### API Signatures

```python
from pathlib import Path
import numpy as np
from typing import Dict

def load_h_e1_feedback(
    cache_dir: Path,
    dataset_name: str
) -> Dict[str, np.ndarray]:
    """
    Load exec/ai/human from h-e1 cache.
    
    Returns: {"exec": [N], "ai": [N], "human": [N]}
    """
    ...

def validate_integrity(feedback: Dict[str, np.ndarray]) -> None:
    """Check no NaN, valid ranges. Raises on error."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | numpy load | Read .npy files |
| L-1-2 | Validation | Check NaN, shapes, ranges |
| L-1-3 | Error handling | Fail-fast on missing files |

---

## M2: ANOVA Testing [Complexity: 12, Budget: 3]

**Applied**: scipy f_oneway on bootstrap distributions

### API Signatures

```python
from scipy.stats import f_oneway
import numpy as np
from typing import Tuple

def compute_correlation_distributions(
    exec_scores: np.ndarray,
    human_ratings: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42
) -> np.ndarray:
    """Bootstrap correlation distribution. Returns: [B] correlations."""
    ...

def anova_test(
    corr_dist_humaneval: np.ndarray,
    corr_dist_mbpp: np.ndarray,
    corr_dist_swebench: np.ndarray
) -> Tuple[float, float]:
    """One-way ANOVA. Returns: (f_stat, p_value)."""
    ...
```

### Pseudo-code

```
compute_correlation_distributions(exec, human, n_bootstrap):
  1. rs = []
  2. For i in range(n_bootstrap):
       indices = random.choice(N, N, replace=True)
       r, _ = pearsonr(exec[indices], human[indices])
       rs.append(r)
  3. Return np.array(rs)

anova_test(dist1, dist2, dist3):
  1. f_stat, p = f_oneway(dist1, dist2, dist3)
  2. Return (f_stat, p)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Bootstrap sampling | Resample with replacement |
| L-2-2 | f_oneway call | scipy.stats wrapper |
| L-2-3 | Effect size computation | abs(r1 - r2) |

---

## M3: Variance Analysis [Complexity: 9, Budget: 3]

**Applied**: numpy variance computation

### API Signatures

```python
def compute_between_task_variance(correlations: Dict[str, float]) -> float:
    """Variance across dataset r values."""
    ...

def compute_within_task_variance(
    corr_distributions: Dict[str, np.ndarray]
) -> float:
    """Mean variance within bootstrap distributions."""
    ...

def compute_variance_ratio(between_var: float, within_var: float) -> float:
    """Between/within ratio (threshold: ≥2.0)."""
    ...
```

### Pseudo-code

```
compute_between_task_variance(correlations):
  1. r_values = [correlations[ds] for ds in datasets]
  2. Return np.var(r_values)

compute_within_task_variance(corr_distributions):
  1. within_vars = [np.var(dist) for dist in corr_distributions.values()]
  2. Return np.mean(within_vars)

compute_variance_ratio(between, within):
  1. Return between / within
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Between variance | np.var on r values |
| L-3-2 | Within variance | Mean of per-dataset variances |
| L-3-3 | Ratio computation | between/within |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

Verified from: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_dl4c/docs/youra_research/h-e1/code/

```python
# From: h-e1/code/data/loader.py (ACTUAL CODE)
from dataclasses import dataclass
from typing import List

@dataclass
class Problem:
    id: str
    prompt: str
    tests: List[str]
    dataset: str

# From: h-e1/code/analysis/correlations.py (ACTUAL CODE)
import numpy as np
from typing import Dict, Tuple

def compute_pairwise_correlations(
    exec: np.ndarray,
    ai: np.ndarray,
    human: np.ndarray
) -> Dict[str, Tuple[float, float]]:
    """Compute all pairwise correlations. Returns {pair: (r, p)}."""
    ...

def bootstrap_ci(
    data1: np.ndarray,
    data2: np.ndarray,
    n_iter: int = 1000,
    seed: int = 42
) -> Tuple[float, float]:
    """Bootstrap 95% CI for Pearson r. Returns (ci_lower, ci_upper)."""
    ...
```

**Note**: Parameter names verified from actual code implementation.

---

## Main Orchestration

### API Signatures

```python
def run_analysis():
    # 1. Load h-e1 feedback data
    datasets = ["humaneval", "mbpp", "swebench"]
    h_e1_cache = Path(".../h-e1/.data_cache/feedback")
    feedback = {ds: load_h_e1_feedback(h_e1_cache, ds) for ds in datasets}
    
    # 2. Validate data integrity
    for ds in datasets:
        validate_integrity(feedback[ds])
    
    # 3. Compute correlations per dataset
    from scipy.stats import pearsonr
    correlations = {}
    for ds in datasets:
        r, p = pearsonr(feedback[ds]["exec"], feedback[ds]["human"])
        ci = bootstrap_ci(feedback[ds]["exec"], feedback[ds]["human"])
        correlations[ds] = {"r": r, "p": p, "ci": ci}
    
    # 4. Bootstrap distributions for ANOVA
    corr_distributions = {
        ds: compute_correlation_distributions(
            feedback[ds]["exec"], feedback[ds]["human"]
        )
        for ds in datasets
    }
    
    # 5. ANOVA test
    f_stat, p_anova = anova_test(
        corr_distributions["humaneval"],
        corr_distributions["mbpp"],
        corr_distributions["swebench"]
    )
    
    # 6. Effect size (competitive vs realistic)
    effect_size = abs(
        correlations["humaneval"]["r"] - correlations["swebench"]["r"]
    )
    
    # 7. Variance decomposition
    between_var = compute_between_task_variance(
        {ds: correlations[ds]["r"] for ds in datasets}
    )
    within_var = compute_within_task_variance(corr_distributions)
    variance_ratio = compute_variance_ratio(between_var, within_var)
    
    # 8. Generate 04_validation.md
    write_report(correlations, p_anova, effect_size, variance_ratio)
```

---

## Total Budget Usage

| Task | Complexity | Budget | Used |
|------|------------|--------|------|
| M1: Feedback Loading | 7 | 3 | 3 |
| M2: ANOVA Testing | 12 | 3 | 3 |
| M3: Variance Analysis | 9 | 3 | 3 |
| **TOTAL** | **28** | **9** | **9** |

---

**Document Version:** 1.0
**Next Phase:** Phase 4 Implementation
