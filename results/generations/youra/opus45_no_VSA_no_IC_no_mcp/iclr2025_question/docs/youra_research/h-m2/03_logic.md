# Logic: H-M2 (MECHANISM)

Applied: uncertainty-quantification-pipeline (consistency-correctness distribution comparison, effect size + significance testing)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code (architecture phase); h-e1's actual output is `outputs/scores.csv` (columns: `question_id, entropy, consistency, label`), not the three JSON files PRD's Data Specs section claims. h-e1's `evaluate.py` exposes only `compute_auroc`/`bootstrap_ci` (AUROC-specific) — no group-comparison utilities to reuse. h-m2 loads the CSV directly and implements Cohen's d / t-test itself.
**Analyzed Path**: `docs/youra_research/h-e1/code/` (no active code present at time of analysis — inherited finding from `03_architecture.md` Serena pass; symbol-level lookup would target `h-e1/code/evaluate.py::compute_auroc`, `h-e1/code/evaluate.py::bootstrap_ci`, `h-e1/code/config.py` once code exists)
**Relevant Symbols**: `evaluate.compute_auroc`, `evaluate.bootstrap_ci` (not reused — AUROC-specific, not group comparison)

All tasks are Low complexity (budget: 0 subtasks — no decomposition needed).

---

## B-1..B-2: Load + Partition [Complexity: 5, 3 / Budget: 0]

**Applied**: pandas CSV ingestion, boolean-mask partition (standard pattern, no KB search needed for this trivial IO)

### API Signatures

```python
def load_scores(csv_path: str) -> pd.DataFrame:
    """Load h-e1 scores.csv. Raises FileNotFoundError with actionable message if missing."""
    ...

def partition_by_label(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Split 'consistency' column by 'label' (0=correct, 1=incorrect).
    Returns (consistency_correct [Nc], consistency_incorrect [Ni])."""
    ...
```

### Pseudo-code

```
1. df = pd.read_csv(csv_path)  # columns: question_id, entropy, consistency, label
2. assert {"question_id","entropy","consistency","label"} <= set(df.columns)
3. correct = df.loc[df.label == 0, "consistency"].to_numpy()
4. incorrect = df.loc[df.label == 1, "consistency"].to_numpy()
5. return correct, incorrect
```

---

## B-3: Cohen's d + Pooled Std + 95% CI [Complexity: 6 / Budget: 0]

**Applied**: uncertainty-quantification-pipeline (standard Cohen's d with pooled variance)

### API Signatures

```python
def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Cohen's d = (mean1 - mean2) / pooled_std."""
    ...

def cohens_d_ci(group1: np.ndarray, group2: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    """95% CI for Cohen's d via standard error approximation. Returns (lo, hi)."""
    ...
```

### Pseudo-code

```
1. n1, n2 = len(group1), len(group2)
2. pooled_std = sqrt(((n1-1)*var(group1, ddof=1) + (n2-1)*var(group2, ddof=1)) / (n1+n2-2))
3. d = (mean(group1) - mean(group2)) / pooled_std
4. se_d = sqrt((n1+n2)/(n1*n2) + d**2/(2*(n1+n2)))
5. z = 1.96  # alpha=0.05
6. return d - z*se_d, d + z*se_d
```

---

## B-4: Independent T-Test [Complexity: 4 / Budget: 0]

**Applied**: scipy.stats.ttest_ind (Welch not required — pooled std already assumed for d)

### API Signatures

```python
def run_ttest(group1: np.ndarray, group2: np.ndarray) -> tuple[float, float]:
    """scipy.stats.ttest_ind(group1, group2). Returns (t_statistic, p_value)."""
    ...
```

---

## B-3+B-4 Combined: analyze_stability_link

### API Signature

```python
def analyze_stability_link(df: pd.DataFrame, alpha: float = 0.05) -> dict:
    """Full pipeline: partition -> cohens_d -> ttest.
    Returns {mean_correct, mean_incorrect, std_correct, std_incorrect,
             cohens_d, cohens_d_ci: (lo, hi), t_stat, p_value,
             significant: bool, direction_correct: bool}."""
    ...
```

### Tensor/Data Shapes

| Variable | Shape | Note |
|----------|-------|------|
| consistency_correct | [Nc] | Nc = count(label==0), float64 |
| consistency_incorrect | [Ni] | Ni = count(label==1), float64 |
| Nc + Ni | 817 | full TruthfulQA generation split |

---

## B-5: Distribution Box/Violin Plot [Complexity: 4 / Budget: 0]

**Applied**: matplotlib standard boxplot/violinplot side-by-side

### API Signature

```python
def plot_distribution_comparison(
    consistency_correct: np.ndarray,
    consistency_incorrect: np.ndarray,
    path: str,
) -> None:
    """Side-by-side box + violin, labels 'Correct'/'Incorrect'. Saves PNG to path."""
    ...
```

---

## B-6: Histogram Overlay [Complexity: 3 / Budget: 0]

### API Signature

```python
def plot_histogram_overlay(
    consistency_correct: np.ndarray,
    consistency_incorrect: np.ndarray,
    path: str,
) -> None:
    """Overlaid alpha-blended histograms, correct vs incorrect. Saves PNG to path."""
    ...
```

---

## B-7: Main Pipeline + Gate Check [Complexity: 6 / Budget: 0]

### API Signature

```python
def main() -> None:
    """
    1. df = load_scores(config.H_E1_SCORES_CSV)
    2. correct, incorrect = partition_by_label(df)
    3. result = analyze_stability_link(df)
    4. json.dump(result, open(f"{OUTPUT_DIR}/metrics.json", "w"))
    5. plot_distribution_comparison(correct, incorrect, f"{FIGURES_DIR}/distribution.png")
    6. plot_histogram_overlay(correct, incorrect, f"{FIGURES_DIR}/histogram.png")
    7. gate_pass = result["direction_correct"] and result["cohens_d"] > COHENS_D_THRESHOLD
    8. print PASS/PIVOT decision; exit 0 if pass else exit 1
    """
    ...
```

### Gate Logic

```
direction_correct = mean_incorrect < mean_correct
gate_pass = direction_correct AND cohens_d > 0.2
```

---

## External Dependencies API (Base Hypothesis)

```python
# From: h-e1 outputs (data artifact, not a code import)
# h-e1/outputs/scores.csv — read via pandas.read_csv, NOT via imported function
# columns: question_id: str, entropy: float, consistency: float, label: int (0=correct, 1=incorrect)
```

**Verified from**: `docs/youra_research/h-e1/code/` and `03_architecture.md` Serena analysis. h-e1's `evaluate.py::compute_auroc` / `evaluate.py::bootstrap_ci` are AUROC-specific and NOT reused — h-m2 implements its own `cohens_d`/`run_ttest` per PRD FR4/FR5.

**Open item for Phase 4**: exact relative path from `code/h-m2/` to `h-e1/outputs/scores.csv` depends on final directory layout (sibling `code/h-e1/` vs `code/h-m2/`) — confirm `H_E1_SCORES_CSV` in `config.py` at implementation time.
