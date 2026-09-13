# Logic: H-M2 Scale-Ensemble Outperformance

**Applied**: mlxtend `mcnemar_table`/`mcnemar` exact-test paired comparison (standard PyTorch/sklearn ecosystem pattern) — no closer KB match found (searched "McNemar test ensemble voting", best hits were unrelated diffusion/image-editing repos).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: `h-e1/code/` does not exist (glob confirmed 0 files) — H-E1 produced only data artifacts (`results.csv`), no importable Python modules. Serena symbol search skipped per architecture doc; H-M2 consumes H-E1 via `pandas.read_csv`, not Python imports.
**Analyzed Path**: `h-e1/code/` (empty)
**Relevant Symbols**: None — new implementation from scratch.

---

## A-1: Data Loading [Complexity: 6, Budget: 6]

**Applied**: dataclass + pandas pivot pattern

### API Signatures

```python
# data.py
from dataclasses import dataclass

@dataclass
class EnsembleInput:
    problem_id: str
    verdicts: dict[str, bool]   # {"7b": bool, "70b": bool, "proprietary": bool}
    ground_truth: bool

def load_he1_verdicts(path: str = "../h-e1/code/results.csv") -> list[EnsembleInput]:
    """Load H-E1 results.csv, pivot long->wide per problem_id."""
    ...

def verify_coverage(inputs: list[EnsembleInput], n_expected: int = 164) -> bool:
    """Assert len(inputs) == n_expected and all 3 judges present per problem."""
    ...
```

### Pseudo-code

```
1. df = pd.read_csv(path)  # columns: problem_id, model, verdict, ground_truth
2. group by problem_id -> verdicts = {model: verdict}, ground_truth = first row's gt
3. inputs = [EnsembleInput(pid, verdicts, gt) for each group]
4. verify_coverage: len(inputs) == 164 and all(len(x.verdicts) == 3 for x in inputs)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A1-1 | load_he1_verdicts | Read CSV, pivot to EnsembleInput list |
| L-A1-2 | verify_coverage | Assert 164/164 + 3-judge completeness, raise on mismatch |

---

## A-2: Best Single Judge [Complexity: 5, Budget: 5]

```python
# baselines.py
def per_judge_accuracy(inputs: list[EnsembleInput]) -> dict[str, float]:
    """Accuracy per judge tier. Returns {"7b": 0.xx, "70b": 0.xx, "proprietary": 0.xx}"""
    ...

def per_judge_fpr_fnr(inputs: list[EnsembleInput]) -> dict[str, dict[str, float]]:
    """Returns {"7b": {"fpr": .., "fnr": ..}, ...}"""
    ...

def best_single_judge(accuracies: dict[str, float]) -> tuple[str, float]:
    """(judge_name, accuracy) with max accuracy."""
    ...

def random_avg_baseline(accuracies: dict[str, float]) -> float:
    """Mean of per-judge accuracies (AB4 expected value)."""
    ...
```

Uses only existing modules — no new subtasks under A-1/A-2 budget beyond A-1 (2-subtask cap already spent).

---

## A-3/A-4/A-5: Ensemble Methods (AB1-AB4)

```python
# ensemble.py
def majority_vote(verdicts: dict[str, bool]) -> bool:
    """2-of-3 majority. sum(votes) >= 2"""
    return sum(verdicts.values()) >= 2

def weighted_majority(verdicts: dict[str, bool], weights: dict[str, float]) -> bool:
    """Weight by per-tier accuracy (from per_judge_accuracy). Threshold > 0.5*sum(weights)."""
    ...

def unanimous_flag(verdicts: dict[str, bool]) -> bool:
    """True iff all 3 judges agree."""
    return len(set(verdicts.values())) == 1

def two_tier_subset(verdicts: dict[str, bool], exclude: str = "7b") -> bool:
    """AB3: majority of remaining 2 judges (exact tie broken by proprietary)."""
    ...

def random_ensemble(verdicts: dict[str, bool], rng: np.random.Generator) -> bool:
    """AB4: rng.choice among the 3 verdict values."""
    return rng.choice(list(verdicts.values()))
```

---

## A-6: McNemar Statistical Test [Complexity: 9, Budget: 9]

**Applied**: mlxtend exact McNemar for small discordant-pair counts (n<25)

### API Signatures

```python
# stats.py
from mlxtend.evaluate import mcnemar_table, mcnemar
import numpy as np

def compare_ensemble_vs_best(
    y_true: np.ndarray,       # [164] bool
    y_ensemble: np.ndarray,   # [164] bool
    y_best_single: np.ndarray # [164] bool
) -> dict:
    """McNemar exact test, ensemble vs best single judge."""
    ...
    # returns {contingency_table: np.ndarray[2,2], chi2: float, p_value: float,
    #          acc_ensemble: float, acc_best_single: float, improvement_pct: float,
    #          ci_95: tuple[float,float], hypothesis_supported: bool}

def pivot_analysis(inputs: list[EnsembleInput], ensemble_fn) -> dict:
    """Split accuracy: unanimous-verdict subset vs split-verdict subset."""
    ...
    # returns {unanimous_acc: float, unanimous_n: int, split_acc: float, split_n: int}
```

### Pseudo-code

```
compare_ensemble_vs_best:
1. tb = mcnemar_table(y_true, y_ensemble, y_best_single)  # 2x2 [[both_correct, ens_only], [best_only, both_wrong]]
2. chi2, p_value = mcnemar(tb, exact=True)
3. acc_ensemble = (y_ensemble == y_true).mean()
4. acc_best = (y_best_single == y_true).mean()
5. improvement = (acc_ensemble - acc_best) * 100
6. ci_95 = wilson_ci(improvement, n=164)  # or bootstrap CI over paired diffs
7. hypothesis_supported = improvement >= 3.0 and p_value < 0.05
```

### Subtasks [these count toward architecture doc's per-task breakdown, not the 2-task H-M2 module budget]

*(Budget note: task allocation caps H-M2 logic doc at 2 subtasks total — A-1's two subtasks above fulfill that budget. A-6/A-7/A-8/A-9 use direct signatures without further subtask decomposition.)*

---

## A-7: Pivot & Unanimous Analysis

Covered by `pivot_analysis` above (A-6 section) — reused, no separate module needed.

---

## A-8: Orchestration (`train.py`)

```python
def main() -> None:
    inputs = load_he1_verdicts()
    verify_coverage(inputs, 164)
    accs = per_judge_accuracy(inputs)
    best_judge, best_acc = best_single_judge(accs)

    results = {}
    for name, fn in [("AB1_majority", majority_vote),
                      ("AB2_weighted", lambda v: weighted_majority(v, accs)),
                      ("AB3_2tier", two_tier_subset),
                      ("AB4_random", lambda v: random_ensemble(v, rng))]:
        y_ens = np.array([fn(x.verdicts) for x in inputs])
        y_best = np.array([x.verdicts[best_judge] for x in inputs])
        y_true = np.array([x.ground_truth for x in inputs])
        results[name] = compare_ensemble_vs_best(y_true, y_ens, y_best)
        results[name]["pivot"] = pivot_analysis(inputs, fn)

    save_csv(results, "comparison.csv")
    save_json(results, "mcnemar_results.json")
```

---

## A-9: Evaluation & Figures

```python
# evaluate.py
def summarize_methods(results: dict) -> pd.DataFrame:
    """Columns: method, acc, improvement_pct, p_value, hypothesis_supported."""
    ...

def plot_accuracy_comparison(df: pd.DataFrame, path: str) -> None: ...
def plot_contingency_heatmap(tb: np.ndarray, path: str) -> None: ...
def plot_pivot_breakdown(pivot: dict, path: str) -> None: ...
```

### Tensor/Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| y_true, y_ensemble, y_best_single | [164] bool | Per-problem correctness |
| contingency_table | [2, 2] int | mcnemar_table output |

---

## External Dependencies (Base Hypothesis)

No Python API dependency — H-E1 has no `code/` module tree. Data-only dependency:

| Artifact | Path | Format |
|----------|------|--------|
| Judge verdicts + ground truth | `h-e1/code/results.csv` | columns: `problem_id, model, verdict, ground_truth` |

**Verified from**: `h-e1/code/` directory (glob returned no files) + H-E1 architecture doc description of `train.py` output schema. Loaded via `pandas.read_csv`, no import required.
