# Logic: H-M2
# Spearman Correlation — Embedding Alignment vs Pass@1 Rank

Applied: Standard scipy permutation_test pattern (pairings mode, n=4)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (consuming H-E1 + H-E2 outputs)
**Status**: API signatures verified from actual H-E1 code and data files
**Analyzed Path**: `docs/youra_research/h-e1/code/src/h_e1/run_experiment.py`, `similarity.py`
**Relevant Symbols**:
- `main()` in run_experiment.py → saves `sim_matrices_serializable = {enc: mat.tolist() ...}` under key `"sim_matrices"`
- `SOURCES = ["humaneval_train", "mbpp_train", "leetcode", "equal_mix"]` (similarity.py)
- `BENCHMARKS = ["humaneval_plus", "mbpp_plus"]` (similarity.py)

---

## External Dependencies API

### H-E1 JSON Schema (verified from actual file + run_experiment.py)

```python
# docs/youra_research/h-e1/experiment_results.json
{
    "sim_matrices": {
        "codebert": [[0.974, 0.948], [0.955, 0.972], [0.909, 0.946], [0.946, 0.954]],  # list(4×list(2))
        "minilm":   [[0.311, 0.276], [0.270, 0.282], [0.247, 0.246], [0.276, 0.266]],
    },
    "sources":    ["humaneval_train", "mbpp_train", "leetcode", "equal_mix"],
    "benchmarks": ["humaneval_plus", "mbpp_plus"],
}
# Row i = sources[i], Col j = benchmarks[j]
# codebert range: 0.909–0.974; minilm range: 0.247–0.311
```

### H-E2 CSV Schema (verified from architecture agent)

```
File: docs/youra_research/h-e2/results/all_results.csv
Columns: condition, seed, benchmark, pass1, n_problems
condition values: humaneval_only | mbpp_only | leetcode_only | equal_mix
benchmark values: "humaneval" ONLY (mbpp rows absent — CANNOT_TEST)
seeds: 42, 123, 777
```

### Condition Alignment Map

| Row | H-E1 sources key   | H-E2 condition value | Array index |
|-----|--------------------|----------------------|-------------|
|  0  | humaneval_train    | humaneval_only       | 0           |
|  1  | mbpp_train         | mbpp_only            | 1           |
|  2  | leetcode           | leetcode_only        | 2           |
|  3  | equal_mix          | equal_mix            | 3           |

| Col | H-E1 benchmarks key | H-E2 benchmark value | Status      |
|-----|---------------------|----------------------|-------------|
|  0  | humaneval_plus      | humaneval            | AVAILABLE   |
|  1  | mbpp_plus           | (absent from CSV)    | CANNOT_TEST |

---

## A-2: Data Loader [Complexity: Low, Budget: 2 subtasks]

### Subtasks [2/2 used]

| ID    | Subtask          | Description                                                              |
|-------|------------------|--------------------------------------------------------------------------|
| L-2-1 | H-E1 JSON Loader | load_h_e1_similarities — parse nested list, np.array, verify shape (4,2) |
| L-2-2 | H-E2 CSV Loader  | load_h_e2_pass_at_1 — groupby mean, pivot to (4,2), fill NaN for mbpp col |

### API Signatures

```python
# code/data_loader.py
import json
import numpy as np
import pandas as pd

H_E1_RESULTS = "docs/youra_research/h-e1/experiment_results.json"
H_E2_CSV     = "docs/youra_research/h-e2/results/all_results.csv"
H_C1_JSON    = "docs/youra_research/h-c1/results/pass_at_1_7b.json"  # optional

SOURCES    = ["humaneval_train", "mbpp_train", "leetcode", "equal_mix"]
BENCHMARKS = ["humaneval_plus", "mbpp_plus"]
CONDITIONS = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
# CONDITIONS[i] aligns with SOURCES[i] — same condition, different naming convention
H_E2_BENCH_MAP = {"humaneval": 0}  # col 1 stays NaN (mbpp absent)


def load_h_e1_similarities(results_path: str = H_E1_RESULTS) -> dict[str, np.ndarray]:
    """Load sim matrices. Returns {'codebert': ndarray(4,2), 'minilm': ndarray(4,2)}."""
    # json.load -> data["sim_matrices"]["codebert"] is list(4×list(2))
    # np.array(..., dtype=np.float32); assert shape == (4, 2)
    ...


def load_h_e2_pass_at_1(results_path: str = H_E2_CSV) -> np.ndarray:
    """Load H-E2 CSV, mean pass1 across seeds. Returns ndarray(4, 2).
    Col 0 = humaneval (averaged seeds). Col 1 = np.nan (mbpp CANNOT_TEST).
    Row order matches CONDITIONS list."""
    # df = pd.read_csv(results_path)
    # pivot = df.groupby(["condition","benchmark"])["pass1"].mean().unstack("benchmark")
    # out = np.full((4, 2), np.nan)
    # for i, cond in enumerate(CONDITIONS): out[i, 0] = pivot.loc[cond, "humaneval"]
    # return out
    ...


def load_h_c1_pass_at_1(results_path: str = H_C1_JSON) -> np.ndarray | None:
    """Returns ndarray(4, 2) if H-C1 file exists, else None."""
    ...


def validate_inputs(
    sim_matrices: dict[str, np.ndarray],  # {'codebert': (4,2), 'minilm': (4,2)}
    pass_mat: np.ndarray,                 # (4,2)
) -> None:
    """Assert shapes; log which benchmark cols are all-NaN (CANNOT_TEST)."""
    ...
```

### Tensor Shapes

| Variable          | Shape  | Note                                       |
|-------------------|--------|--------------------------------------------|
| sim_matrices[enc] | (4, 2) | float32, rows=conditions, cols=benchmarks  |
| pass_mat          | (4, 2) | float64, col 1 all NaN (mbpp CANNOT_TEST)  |
| sim_vec (cell)    | (4,)   | column slice of sim_matrices[enc]          |
| pass_vec (cell)   | (4,)   | column slice of pass_mat; may contain NaN  |

---

## A-3: Statistical Analysis [Complexity: Medium, Budget: 2 subtasks]

### Subtasks [2/2 used]

| ID    | Subtask               | Description                                                      |
|-------|-----------------------|------------------------------------------------------------------|
| L-3-1 | Permutation Test Core | run_spearman_permutation_test + bootstrap_ci + NaN/tie handling  |
| L-3-2 | Cell Iterator + Gate  | run_all_cells (encoder×benchmark×model_size) + evaluate_gate     |

### Dataclasses

```python
# code/analysis.py
from dataclasses import dataclass
from typing import Optional
import numpy as np
from scipy import stats

BENCHMARKS = ["humaneval_plus", "mbpp_plus"]


@dataclass
class SpearmanResult:
    rho: float
    pvalue: float
    significant: bool           # pvalue < 0.05
    null_distribution: np.ndarray  # shape (n_resamples,)
    ci_lo: float
    ci_hi: float                # 95% bootstrap CI bounds
    tau: float                  # Kendall tau (supplementary)
    tau_p: float
    can_test: bool              # False if pass_vec all-identical or all-NaN
    used_kendall: bool          # True if Spearman→NaN, fell back to Kendall as primary


@dataclass
class CellResult:
    encoder: str                # "codebert" | "minilm"
    benchmark: str              # "humaneval_plus" | "mbpp_plus"
    benchmark_col: int          # 0 | 1
    model_size: str             # "1b" | "7b"
    sim_vec: np.ndarray         # (4,)
    pass_vec: np.ndarray        # (4,)
    result: Optional[SpearmanResult]  # None if can_test=False
    status: str                 # "TESTED" | "CANNOT_TEST"


@dataclass
class GateEvaluation:
    gate_status: str            # "SATISFIED" | "FALSIFIED" | "CANNOT_TEST"
    satisfied_cells: list[str]  # "encoder/benchmark/model_size" for rho>0 and p<0.05
    concordant_benchmarks: list[str]  # benchmarks where both encoders have rho>0
    reason: str
```

### API Signatures

```python
def run_spearman_permutation_test(
    sim_vector: np.ndarray,   # shape (4,) — similarities for one benchmark column
    pass_vector: np.ndarray,  # shape (4,) — pass@1 for one benchmark column
    n_resamples: int = 10000,
    random_state: int = 42,
) -> SpearmanResult:
    """Permutation test (pairings). Falls back to Kendall if Spearman returns NaN (ties)."""
    ...


def bootstrap_ci(
    sim_vector: np.ndarray,   # (4,)
    pass_vector: np.ndarray,  # (4,)
    n_bootstrap: int = 1000,
    random_state: int = 42,
) -> tuple[float, float]:
    """95% bootstrap CI for Spearman rho. Returns (ci_lo, ci_hi)."""
    ...


def run_all_cells(
    sim_matrices: dict[str, np.ndarray],   # {'codebert': (4,2), 'minilm': (4,2)}
    pass_matrices: dict[str, np.ndarray],  # {'1b': (4,2)}; '7b' key optional/None value
    benchmarks: list[str] = BENCHMARKS,
    encoders: list[str] = ["codebert", "minilm"],
    model_sizes: list[str] = ["1b"],
) -> list[CellResult]:
    """Iterate (encoder × benchmark × model_size). Mark CANNOT_TEST if pass_vec all-NaN."""
    ...


def evaluate_gate(cell_results: list[CellResult]) -> GateEvaluation:
    """Evaluate gate: SATISFIED if rho>0 and p<0.05 for >=1 cell AND dual-encoder concordance.
    CANNOT_TEST if all cells are CANNOT_TEST. FALSIFIED otherwise."""
    ...
```

### Pseudo-code: run_spearman_permutation_test

```
1. NaN/identical check:
       if np.all(np.isnan(pass_vector)) or len(np.unique(pass_vector[~np.isnan(pass_vector)])) < 2:
           return SpearmanResult(can_test=False, rho=np.nan, pvalue=np.nan, ...)

2. Permutation test (scipy):
       def statistic(x):
           return stats.spearmanr(x, pass_vector).statistic
       perm = stats.permutation_test(
           (sim_vector,), statistic,
           permutation_type='pairings',
           n_resamples=n_resamples,
           alternative='greater',
           random_state=random_state,
       )
       rho, pvalue, null_dist = perm.statistic, perm.pvalue, perm.null_distribution

3. Tie fallback:
       tau, tau_p = stats.kendalltau(sim_vector, pass_vector, alternative='greater')
       if np.isnan(rho):
           rho, pvalue, used_kendall = tau, tau_p, True
       else:
           used_kendall = False

4. Bootstrap CI:
       ci_lo, ci_hi = bootstrap_ci(sim_vector, pass_vector, random_state=random_state)

5. return SpearmanResult(rho, pvalue, pvalue<0.05, null_dist, ci_lo, ci_hi,
                         tau, tau_p, can_test=True, used_kendall=used_kendall)
```

### Pseudo-code: evaluate_gate

```
tested = [c for c in cell_results if c.status == "TESTED"]
if not tested:
    return GateEvaluation("CANNOT_TEST", [], [], "all cells CANNOT_TEST")

satisfied = [c for c in tested if c.result.rho > 0 and c.result.significant]

concordant_benchmarks = []
for bm in set(c.benchmark for c in tested):
    cells_bm = [c for c in tested if c.benchmark == bm]
    if all(enc in {c.encoder for c in cells_bm if c.result.rho > 0}
           for enc in ["codebert", "minilm"]):
        concordant_benchmarks.append(bm)

supporting = [c for c in satisfied if c.benchmark in concordant_benchmarks]

if supporting:
    return GateEvaluation("SATISFIED", [cell_id(c) for c in supporting],
                          concordant_benchmarks, "rho>0, p<0.05, dual-encoder concordance")
else:
    return GateEvaluation("FALSIFIED", [], [], "no cell: rho>0 AND p<0.05 with concordance")
```
