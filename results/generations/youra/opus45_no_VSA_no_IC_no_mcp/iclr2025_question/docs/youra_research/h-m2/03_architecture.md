# Architecture: H-M2 (MECHANISM)

Applied: uncertainty-quantification-pipeline (consistency-correctness distribution analysis, reused from h-e1 KB pattern)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Actual code found at h-e1/code/ — differs from PRD's stated artifact names
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: h-e1 does NOT produce `generated_responses.json`, `consistency_scores.json`, or `correctness_labels.json` as PRD FR1/Data Specs claim. Actual output is a single `outputs/scores.csv` with columns `question_id, entropy, consistency, label` (label: 0=correct, 1=hallucinated, matches h-m2 convention). h-m2 must load this CSV directly — no need to reconstruct raw responses since consistency/labels are precomputed.

---

## File Structure

```
code/h-m2/
  config.py     # fixed paths + thresholds
  analysis.py   # load scores.csv, partition, Cohen's d, t-test
  plots.py      # box/violin + histogram overlay
  run.py        # entrypoint
```

MECHANISM analysis-only PoC: no model/data loading, no training. Reuses h-e1 CSV directly.

---

## Modules

### config.py

```python
H_E1_SCORES_CSV = "../h-e1/outputs/scores.csv"  # question_id, entropy, consistency, label
OUTPUT_DIR = "outputs"
FIGURES_DIR = "figures"
COHENS_D_THRESHOLD = 0.2
ALPHA = 0.05
```

### analysis.py (`code/h-m2/analysis.py`)

**Dependencies**: config, pandas, numpy, scipy

```python
def load_scores(csv_path: str) -> pd.DataFrame:
    """Load h-e1 scores.csv (question_id, entropy, consistency, label)."""

def partition_by_label(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Returns (consistency_correct, consistency_incorrect) arrays, label 0=correct 1=incorrect."""

def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float: ...

def run_ttest(group1: np.ndarray, group2: np.ndarray) -> tuple[float, float]:
    """Returns (t_statistic, p_value)."""

def analyze_stability_link(df: pd.DataFrame) -> dict:
    """Returns {mean_correct, mean_incorrect, cohens_d, t_stat, p_value, direction_correct}."""
```

### plots.py (`code/h-m2/plots.py`)

**Dependencies**: matplotlib, numpy

```python
def plot_distribution_comparison(consistency_correct: np.ndarray, consistency_incorrect: np.ndarray, path: str) -> None:
    """Box/violin plot, correct vs incorrect."""

def plot_histogram_overlay(consistency_correct: np.ndarray, consistency_incorrect: np.ndarray, path: str) -> None: ...
```

### run.py (`code/h-m2/run.py`)

**Dependencies**: all above modules

```python
def main() -> None:
    """
    Load h-e1/outputs/scores.csv -> partition by label ->
    analyze_stability_link -> save metrics.json ->
    plot_distribution_comparison + plot_histogram_overlay ->
    gate check (direction correct AND cohens_d > 0.2)
    """
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| scores.csv (data) | N/A — read via `pandas.read_csv` | `h-e1/code/outputs/scores.csv` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual `run.py`, `config.py`) — h-e1 has no importable analysis functions worth reusing (AUROC-specific); h-m2 reimplements Cohen's d/t-test directly per its own spec (h-e1's evaluate.py only has `compute_auroc`/`bootstrap_ci`, not group comparison).

**Note**: Exact relative path from h-m2 code dir to h-e1's `outputs/scores.csv` must be confirmed at Phase 4 (depends on final code/ layout — sibling `code/h-e1/outputs/` vs `code/h-m2/outputs/`).

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Load h-e1 artifacts | Read scores.csv, validate schema, handle missing file | 5 | 2+2+0+1 |
| B-2 | Partition by label | Split consistency array by correctness label | 3 | 1+1+0+1 |
| B-3 | Cohen's d + pooled std | Effect size calc with 95% CI | 6 | 2+1+2+1 |
| B-4 | Independent t-test | scipy ttest_ind, p-value, significance | 4 | 1+1+1+1 |
| B-5 | Distribution box/violin plot | matplotlib comparison plot, save to figures/ | 4 | 2+1+0+1 |
| B-6 | Histogram overlay plot | Overlaid histogram by correctness | 3 | 1+1+0+1 |
| B-7 | Main pipeline + gate check | Wire B-1..B-6, save metrics.json, PASS/PIVOT decision | 6 | 2+3+0+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [B-1, B-3, B-4, B-5, B-7], VeryLow(<4): [B-2, B-6]

Skipped: model.py, data.py, training loop — h-m2 is pure statistical re-analysis of h-e1's precomputed scores.csv, no inference or new data loading needed.
