# Architecture: H-M2 (Scale-Ensemble Outperformance, MECHANISM)

**Hypothesis:** Majority-vote ensemble across 7B/70B/proprietary judges outperforms best single judge by ≥3% accuracy on HumanEval+.
Applied: McNemar exact-test paired comparison + majority/weighted-vote ensemble pattern (from experiment brief, no closer KB match found)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1) referenced, but no `code/` subfolder exists yet
**Status**: `h-e1/code/` not found — H-E1 produced data artifacts (`results.csv`, `contingency.csv`), not a reusable module tree. Serena symbol search skipped (no code to introspect).
**Analyzed Path**: `h-e1/code/` (glob returned no files)
**Findings**: H-M2 depends on H-E1 **data outputs** (per-problem judge verdicts + ground truth), not H-E1 code. New implementation from scratch, consuming cached CSV.

---

## File Structure

```
h-m2/code/
  config.py       # judge tiers, McNemar threshold, paths to H-E1 outputs
  data.py         # load H-E1 results.csv, reshape to per-problem verdict dict
  ensemble.py      # majority_vote, weighted_majority, unanimous_flag
  baselines.py     # best_single_judge, random_ensemble, codebertscore constant
  stats.py         # mcnemar_table, mcnemar test, CI, pivot analysis
  train.py         # orchestrator: run AB1-AB4 ablations, save comparison.csv
  evaluate.py      # accuracy/FPR/FNR per method + figures
  figures/
```

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
JUDGES = ["7b", "70b", "proprietary"]
HE1_RESULTS_PATH = "../h-e1/code/results.csv"
P_VALUE_THRESHOLD = 0.05
IMPROVEMENT_TARGET = 0.03
CODEBERTSCORE_BASELINE = 0.58
```

### Data (`data.py`)

**Dependencies**: config

```python
@dataclass
class EnsembleInput:
    problem_id: str
    verdicts: dict[str, bool]   # judge -> verdict
    ground_truth: bool

def load_he1_verdicts(path: str) -> list[EnsembleInput]: ...
def verify_coverage(inputs: list[EnsembleInput], n_expected: int = 164) -> bool: ...
```

### Ensemble (`ensemble.py`)

**Dependencies**: data

```python
def majority_vote(verdicts: dict[str, bool]) -> bool: ...
def weighted_majority(verdicts: dict[str, bool], weights: dict[str, float]) -> bool: ...
def unanimous_flag(verdicts: dict[str, bool]) -> bool: ...
def two_tier_subset(verdicts: dict[str, bool], exclude: str = "7b") -> bool: ...  # AB3
def random_ensemble(verdicts: dict[str, bool], rng: np.random.Generator) -> bool: ...  # AB4
```

### Baselines (`baselines.py`)

**Dependencies**: data

```python
def per_judge_accuracy(inputs: list[EnsembleInput]) -> dict[str, float]: ...
def best_single_judge(accuracies: dict[str, float]) -> tuple[str, float]: ...
def random_avg_baseline(accuracies: dict[str, float]) -> float: ...
```

### Stats (`stats.py`)

**Dependencies**: mlxtend, numpy

```python
def compare_ensemble_vs_best(y_true, y_ensemble, y_best_single) -> dict: ...
    # returns {contingency_table, chi2, p_value, acc_ensemble, acc_best_single,
    #          improvement_pct, ci_95, hypothesis_supported}
def pivot_analysis(inputs: list[EnsembleInput], ensemble_fn) -> dict: ...
    # accuracy split: unanimous vs split-verdict subsets
```

### Train / Orchestrator (`train.py`)

**Dependencies**: data, ensemble, baselines, stats

```python
def main() -> None: ...
    # load_he1_verdicts -> verify_coverage(164)
    # per_judge_accuracy -> best_single_judge
    # for method in [AB1 majority, AB2 weighted, AB3 2-tier, AB4 random]:
    #   compute ensemble verdicts -> compare_ensemble_vs_best -> pivot_analysis
    # save comparison.csv, mcnemar_results.json
```

### Evaluate (`evaluate.py`)

**Dependencies**: stats, matplotlib

```python
def summarize_methods(results: dict) -> pd.DataFrame: ...  # acc, improvement, p-value per AB
def plot_accuracy_comparison(df: pd.DataFrame, path: str) -> None: ...
def plot_contingency_heatmap(tb: np.ndarray, path: str) -> None: ...
def plot_pivot_breakdown(pivot: dict, path: str) -> None: ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Data, Not Code)

| Artifact | Path | Notes |
|----------|------|-------|
| Judge verdicts + ground truth | `h-e1/code/results.csv` | Per-problem, per-scale verdict + TP/TN/FP/FN label |
| Contingency/error stats | `h-e1/code/contingency.csv` | Reference for per-tier accuracy (weighted majority weights) |

**Verified from**: `h-e1/code/` directory listing — no Python modules present, only expected data outputs (H-E1 architecture doc confirms `train.py` writes `results.csv`). H-M2 imports data via pandas `read_csv`, not Python imports.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load H-E1 results.csv, reshape to EnsembleInput, verify 164/164 coverage | 6 | 2+2+1+1 |
| A-2 | Best single judge | Per-judge accuracy/FPR/FNR + best single identification | 5 | 1+1+2+1 |
| A-3 | Majority vote (AB1) | Implement + apply simple 2-of-3 majority vote | 4 | 1+1+1+1 |
| A-4 | Weighted majority (AB2) | Weight by H-E1 per-tier accuracy, apply weighted vote | 6 | 2+2+1+1 |
| A-5 | Ablation variants (AB3/AB4) | 2-tier subset + random baseline ensembles | 6 | 2+1+2+1 |
| A-6 | McNemar statistical test | Contingency table, exact McNemar, CI, improvement % | 9 | 2+2+3+2 |
| A-7 | Pivot & unanimous analysis | Accuracy split on unanimous vs split-verdict cases | 6 | 2+1+2+1 |
| A-8 | Orchestration | train.py wiring all AB variants end-to-end, save comparison.csv | 7 | 2+3+1+1 |
| A-9 | Evaluation & figures | Summary table + 3 required visualizations | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-6], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-7, A-8, A-9]
